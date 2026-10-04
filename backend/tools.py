"""Catalogue access and the tools the shop assistant can call.

Everything here is read-only and limited to the `catalogue` and `inventory` tables.
The assistant has no access to accounts or other shoppers' data.
"""

import json
import logging
import math
import os
import re
import sqlite3
import tempfile
import threading
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path

from pydantic_ai import ModelRetry, RunContext
from pydantic_ai.messages import ModelMessage, ModelRequest, ModelResponse, RetryPromptPart, ToolCallPart, ToolReturnPart
from pydantic_core import to_jsonable_python

from models import (
    CategorySummary,
    ChatDeps,
    ChatPage,
    CustomerProfile,
    PageContext,
    PageFilters,
    PageShowing,
    Product,
    ProductDetail,
    ProductCard,
    ProductInfo,
    ProductResult,
    SearchResponse,
    SearchResults,
    SizeAvailability,
    SizeStock,
    StockResult,
    StockStatus,
)

BACKEND_DIR = Path(__file__).resolve().parent
# CAMPUS_CUSTOMS_DATA_DIR can point at a copy of the data pack (useful for testing).
DATA_DIR = Path(os.environ.get("CAMPUS_CUSTOMS_DATA_DIR") or BACKEND_DIR.parent / "data")
DB_PATH = DATA_DIR / "campus_customs.db"

SIZE_ORDER = ["XS", "S", "M", "L", "XL", "XXL"]

# Bump this whenever the photo cleanup in main.py changes, so browsers fetch the new photos
# instead of showing older copies they have cached.
IMAGE_VERSION = "4"
LOW_STOCK_AT_OR_BELOW = 5
PAGE_RESULTS_LIMIT = 150  # cards the Products page can be given for one assistant search
MAX_PAGE_TITLE_LENGTH = 40
SORT_KEYS = ("relevance-desc", "relevance-asc", "price-desc", "price-asc", "name-asc", "name-desc")

# Display-name fixes: the catalogue spells these out as "1 4 Zip" and "T Shirt".
NAME_FIXES = (
    (re.compile(r"\b1 4 Zip\b", re.IGNORECASE), "Quarter-Zip"),
    (re.compile(r"\bT Shirt\b", re.IGNORECASE), "T-Shirt"),
)

# A few catalogue rows carry a pipeline placeholder instead of a real description.
PLACEHOLDER_DESCRIPTION = "Vision blocked"

# Hand-written descriptions (product_id -> text) that replace the catalogue's own. The catalogue has a few rows
# whose description is a pipeline placeholder ("Vision blocked..."); these three were written from the photos.
DESCRIPTION_OVERRIDES: dict[str, str] = {
    "benjamin-franklin-t-shirt": (
        "Heather gray short-sleeve T-shirt featuring a centered Benjamin Franklin College heraldic shield "
        "crest in blue, red, and white, with BENJAMIN FRANKLIN COLLEGE text beneath."
    ),
    "berkeley-sweater-fleece-jacket": (
        "Heather gray full-zip sweater fleece jacket with a stand collar, charcoal gray zipper and pocket "
        "trim, and an embroidered red Berkeley College crest on the left chest."
    ),
    "timothy-dwight-college-crewneck": (
        "Heather gray long-sleeve crewneck sweatshirt with ribbed collar, cuffs, and waistband, featuring "
        "a small Timothy Dwight College crest and TIMOTHY DWIGHT text on the left chest."
    ),
}

# ---------------------------------------------------------------------------
# Catalogue access (also used by the API routes in main.py)
# ---------------------------------------------------------------------------


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def display_name(name: str) -> str:
    for pattern, replacement in NAME_FIXES:
        name = pattern.sub(replacement, name)
    return name


# The catalogue lists 22 color names ("navy blue", "heather gray", "dusty coral", ...). For filtering they are
# grouped into a few families. The first rule that matches wins, so "light blue" is Blue and "navy blue" is Navy.
COLOR_FAMILIES = (
    ("Navy", ("navy",)),
    ("Blue", ("blue",)),
    ("Gray", ("gray", "grey", "charcoal")),
    ("White", ("white",)),
    ("Cream", ("cream", "ivory")),
    ("Red", ("red",)),
    ("Black", ("black",)),
    ("Gold / Yellow", ("gold", "yellow")),
    ("Green", ("green",)),
    ("Coral", ("coral",)),
    ("Multicolor", ("multicolor",)),
)


def color_families(colors: list[str]) -> list[str]:
    found = set()
    for color in colors:
        for family, keywords in COLOR_FAMILIES:
            if any(word in color.lower() for word in keywords):
                found.add(family)
                break
    return [family for family, _ in COLOR_FAMILIES if family in found]


def to_product(row: sqlite3.Row, available_sizes: list[str] | None = None) -> Product:
    # image_file_path is stored relative to data/ (e.g. "products/<id>.jpg").
    description = DESCRIPTION_OVERRIDES.get(row["product_id"], row["description"])
    if PLACEHOLDER_DESCRIPTION in description:
        description = ""
    colors = json.loads(row["colors"])
    return Product(
        product_id=row["product_id"],
        name=display_name(row["name"]),
        garment_type=row["garment_type"],
        description=description,
        colors=colors,
        price=row["price"],
        image_url=f"/images/{Path(row['image_file_path']).name}?v={IMAGE_VERSION}",
        category=category_of(row["garment_type"]),
        color_families=color_families(colors),
        available_sizes=available_sizes or [],
    )


def size_sort_key(size: str) -> int:
    return SIZE_ORDER.index(size) if size in SIZE_ORDER else len(SIZE_ORDER)


def format_price(price: float) -> str:
    return f"${price:,.2f}"


def stock_status(quantity: int) -> StockStatus:
    return "sold out" if quantity == 0 else "low stock" if quantity <= LOW_STOCK_AT_OR_BELOW else "in stock"


def all_products() -> list[Product]:
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue ORDER BY name").fetchall()
    stock = in_stock_sizes()
    return [to_product(r, stock.get(r["product_id"])) for r in rows]


def product_detail(product_id: str) -> ProductDetail | None:
    with connect() as conn:
        row = conn.execute("SELECT * FROM catalogue WHERE product_id = ?", (product_id,)).fetchone()
        if row is None:
            return None
        stock = conn.execute("SELECT size, quantity FROM inventory WHERE product_id = ?", (product_id,)).fetchall()
    sizes = sorted((SizeStock(size=s["size"], quantity=s["quantity"]) for s in stock), key=lambda s: size_sort_key(s.size))
    in_stock = [s.size for s in sizes if s.quantity > 0]
    return ProductDetail(**to_product(row, in_stock).model_dump(), sizes=sizes)


def products_by_ids(product_ids: list[str]) -> list[Product]:
    """The matching products in the order given; unknown ids are dropped."""
    by_id = {p.product_id: p for p in all_products()}
    return [by_id[i] for i in dict.fromkeys(product_ids) if i in by_id]


# ---------------------------------------------------------------------------
# Search helpers
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "for", "and", "or", "with", "in", "of", "to", "me", "my", "i", "do", "you", "have", "any",
    "show", "want", "looking", "find", "something", "some", "that", "is", "it", "on", "under", "over", "than",
    "less", "please", "got", "what", "which", "are", "there", "size", "sizes", "like", "need", "get", "can",
}
SYNONYMS = {"hoody": "hoodie", "sweater": "sweatshirt"}
SIZE_ALIASES = {
    "xs": "XS", "extra small": "XS", "x-small": "XS", "xsmall": "XS",
    "s": "S", "small": "S", "sm": "S",
    "m": "M", "medium": "M", "med": "M",
    "l": "L", "large": "L", "lg": "L",
    "xl": "XL", "extra large": "XL", "x-large": "XL", "xlarge": "XL",
    "xxl": "XXL", "2xl": "XXL", "xx-large": "XXL", "xxlarge": "XXL", "double xl": "XXL",
}
FIELD_WEIGHTS = {"name": 3.0, "garment_type": 3.0, "tags": 2.0, "colors": 2.0, "description": 1.0}
MAX_RESULTS = 10


def normalize_size(text: str) -> str | None:
    return SIZE_ALIASES.get(text.strip().lower())


def stem(token: str) -> str:
    return token[:-1] if len(token) > 3 and token.endswith("s") and not token.endswith("ss") else token


def tokenize(text: str) -> list[str]:
    text = re.sub(r"\b1\s*/\s*4\b|\b1\s+4\b|\bqtr\b", "quarter", text.lower())
    # "T-shirt" is one word, so a search for T-shirts does not also match other kinds of shirt.
    text = re.sub(r"\bt[\s-]?shirts?\b|\btees?\b", "tshirt shirt", text)
    tokens = [stem(t) for t in re.findall(r"[a-z0-9]+", text)]
    return [SYNONYMS.get(t, t) for t in tokens if len(t) > 1 and t not in STOPWORDS]


def category_of(garment_type: str) -> str:
    g = garment_type.lower()
    if "hood" in g:
        return "Hoodies"
    if "quarter" in g:
        return "Quarter-Zips"
    if "jacket" in g:
        return "Jackets"
    if "t-shirt" in g or "t shirt" in g:
        return "T-Shirts"
    if "long-sleeve" in g and "shirt" in g:
        return "Long-Sleeve Performance Shirts"
    return "Sweatshirts"  # crewnecks, mockneck, raglan, etc.


@lru_cache(maxsize=1)
def search_index() -> tuple[list[dict], dict[str, float]]:
    """Searchable text per product (cached: the catalogue does not change while running)."""
    with connect() as conn:
        rows = conn.execute("SELECT * FROM catalogue").fetchall()
    entries = []
    for row in rows:
        product = to_product(row)
        fields = {
            "name": set(tokenize(product.name)),
            "garment_type": set(tokenize(product.garment_type)),
            "tags": set(tokenize(" ".join(json.loads(row["search_tags"])))),
            "colors": set(tokenize(" ".join(product.colors))),
            "description": set(tokenize(product.description)),
        }
        entries.append({"product": product, "fields": fields, "all": set().union(*fields.values())})
    doc_freq: dict[str, int] = {}
    for entry in entries:
        for token in entry["all"]:
            doc_freq[token] = doc_freq.get(token, 0) + 1
    idf = {t: math.log(1 + len(entries) / n) for t, n in doc_freq.items()}
    return entries, idf


def in_stock_sizes() -> dict[str, list[str]]:
    with connect() as conn:
        rows = conn.execute("SELECT product_id, size FROM inventory WHERE quantity > 0").fetchall()
    sizes: dict[str, list[str]] = {}
    for r in rows:
        sizes.setdefault(r["product_id"], []).append(r["size"])
    return {pid: sorted(s, key=size_sort_key) for pid, s in sizes.items()}


# ---------------------------------------------------------------------------
# Tools the agent can call (registered in agent.py)
# ---------------------------------------------------------------------------


def find_products(
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    size: str | None = None,
) -> tuple[list[tuple[Product, list[str]]], str | None]:
    """Every matching product (best match first) with its in-stock sizes, plus the normalized requested size."""
    wanted_size = None
    if size:
        wanted_size = normalize_size(size)
        if wanted_size is None:
            raise ModelRetry(f"'{size}' is not a size we carry. Valid sizes: {', '.join(SIZE_ORDER)}.")
    entries, idf = search_index()
    stock = in_stock_sizes()
    tokens = set(tokenize(query))

    scored = []
    for entry in entries:
        product = entry["product"]
        if max_price is not None and product.price > max_price:
            continue
        if min_price is not None and product.price < min_price:
            continue
        available = stock.get(product.product_id, [])
        matched = tokens & entry["all"]
        if tokens and not matched:
            continue
        score = sum(
            idf[t] * max((w for f, w in FIELD_WEIGHTS.items() if t in entry["fields"][f]), default=0) for t in matched
        )
        scored.append((len(matched) == len(tokens), score, product, available))

    if any(full for full, *_ in scored):  # prefer products that match every keyword
        scored = [s for s in scored if s[0]]
    if tokens:
        # In-stock-in-the-requested-size first, then best keyword match, then cheapest.
        scored.sort(key=lambda s: (bool(wanted_size) and wanted_size not in s[3], -s[1], s[2].price, s[2].name))
    else:
        # No keywords (the whole catalogue): products available in the most sizes first, then A to Z.
        scored.sort(key=lambda s: (bool(wanted_size) and wanted_size not in s[3], -len(s[3]), s[2].name))
    return [(product, available) for _, _, product, available in scored], wanted_size


def search_products(
    query: str = "",
    max_price: float | None = None,
    min_price: float | None = None,
    size: str | None = None,
    limit: int = 6,
) -> SearchResponse:
    """Search the Campus Customs catalogue.

    Use this whenever the shopper asks what we carry or wants recommendations. The reply says how many products
    matched in total (total_matches) and lists the best few. When the shopper asks to browse a type of item,
    the website shows every match as cards on the page, so you do not need to list them all.

    Args:
        query: Free-text keywords such as "navy hoodie", "baseball", "Saybrook", or "quarter zip".
            Leave empty to browse by the filters alone.
        max_price: Only products at or below this price in US dollars.
        min_price: Only products at or above this price in US dollars.
        size: A size the shopper cares about (XS, S, M, L, XL, or XXL; "medium" etc. also work). Products in stock
            in that size are listed first. Products sold out in that size are still returned, marked with
            requested_size_in_stock=false, so say clearly when the size is sold out.
        limit: How many results to return (1-10).
    """
    matches, wanted_size = find_products(query, max_price, min_price, size)
    limit = max(1, min(limit, MAX_RESULTS))
    results = [
        ProductResult(
            product_id=p.product_id,
            name=p.name,
            garment_type=p.garment_type,
            description=p.description,
            colors=p.colors,
            price=p.price,
            price_display=format_price(p.price),
            available_sizes=available,
            sold_out_sizes=[s for s in SIZE_ORDER if s not in available],
            requested_size=wanted_size,
            requested_size_in_stock=(wanted_size in available) if wanted_size else None,
        )
        for p, available in matches[:limit]
    ]
    return SearchResponse(total_matches=len(matches), results=results)


def category_names() -> list[str]:
    return sorted({category_of(p.garment_type) for p in all_products()})


def clean_page_filters(
    categories: list[str] | None,
    sizes: list[str] | None,
    colors: list[str] | None,
    min_price: float | None,
    max_price: float | None,
    sort: str | None,
) -> PageFilters:
    """Check the filter values the assistant picked and turn them into the exact values the page uses."""
    allowed_categories = category_names()
    cleaned_categories = []
    for name in categories or []:
        match = next((c for c in allowed_categories if c.lower() == name.strip().lower()), None)
        if match is None:
            raise ModelRetry(f"'{name}' is not an item type. Use these exactly: {', '.join(allowed_categories)}.")
        cleaned_categories.append(match)
    cleaned_sizes = []
    for text in sizes or []:
        size = normalize_size(text)
        if size is None:
            raise ModelRetry(f"'{text}' is not a size we carry. Valid sizes: {', '.join(SIZE_ORDER)}.")
        cleaned_sizes.append(size)
    family_names = [family for family, _ in COLOR_FAMILIES]
    cleaned_colors = []
    for text in colors or []:
        found = next((f for f in family_names if f.lower() == text.strip().lower()), None) or next(iter(color_families([text])), None)
        if found is None:
            raise ModelRetry(f"'{text}' is not a color we filter by. Use these color families: {', '.join(family_names)}.")
        cleaned_colors.append(found)
    for price in (min_price, max_price):
        if price is not None and price < 0:
            raise ModelRetry("Prices cannot be negative.")
    if min_price is not None and max_price is not None and min_price > max_price:
        raise ModelRetry("min_price is higher than max_price.")
    if sort is not None and sort not in SORT_KEYS:
        raise ModelRetry(f"'{sort}' is not a sort order. Use one of: {', '.join(SORT_KEYS)}.")
    return PageFilters(
        categories=list(dict.fromkeys(cleaned_categories)),
        sizes=list(dict.fromkeys(cleaned_sizes)),
        colors=list(dict.fromkeys(cleaned_colors)),
        min_price=min_price,
        max_price=max_price,
        sort=sort,  # type: ignore[arg-type]
    )


def matches_page_filters(product: Product, available_sizes: list[str], filters: PageFilters) -> bool:
    """The same rules as the filters on the Products page (frontend/src/shopFilters.ts)."""
    if filters.categories and product.category not in filters.categories:
        return False
    if filters.sizes and not any(size in available_sizes for size in filters.sizes):
        return False
    if filters.colors and not any(color in product.color_families for color in filters.colors):
        return False
    if filters.min_price is not None and product.price < filters.min_price:
        return False
    if filters.max_price is not None and product.price > filters.max_price:
        return False
    return True


def build_page_results(
    title: str,
    query: str = "",
    categories: list[str] | None = None,
    sizes: list[str] | None = None,
    colors: list[str] | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
) -> tuple[SearchResults | None, int, list[str]]:
    """What the Products page should show: the products matching `query`, with the filters switched on.

    Returns the results (None when nothing would be shown), how many products the page shows after the
    filters, and a few examples. Used both by the show_on_page tool and by the server when it builds the reply.
    """
    title = title.strip()
    if not title or len(title) > MAX_PAGE_TITLE_LENGTH:
        raise ModelRetry(f"title must be a short label of 1-{MAX_PAGE_TITLE_LENGTH} characters, like 'T-shirts'.")
    filters = clean_page_filters(categories, sizes, colors, min_price, max_price, sort)
    matches, _ = find_products(query)  # the keywords decide the set; sizes, colors, and prices become filters
    shown = [(p, available) for p, available in matches if matches_page_filters(p, available, filters)]
    if not matches or not shown:
        return None, len(shown), []
    results = SearchResults(
        title=title,
        total=len(matches),
        products=[ProductCard.from_product(p) for p, _ in matches[:PAGE_RESULTS_LIMIT]],
        filters=None if filters.is_empty() else filters,
    )
    return results, len(shown), [f"{p.name} ({format_price(p.price)})" for p, _ in shown[:5]]


def show_on_page(
    title: str,
    query: str = "",
    categories: list[str] | None = None,
    sizes: list[str] | None = None,
    colors: list[str] | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort: str | None = None,
) -> PageShowing:
    """Show products on the shopper's Products page, with filters switched on when the request needs them.

    Use this when the shopper asks to browse a kind of item ("what T-shirts do you have?", "navy hoodies in
    medium under $60"). The website swaps its product grid for these products and switches the filters on in
    the filter panel, where the shopper can see them and change them. The reply tells you exactly how many
    products the page now shows, so use that number in your message.

    Put what kind of item it is (hoodie, T-shirt, a college, a sport, a theme) in `query`, and put sizes,
    colors, and prices in the filter arguments instead of in `query`. Leave `query` empty to filter the whole
    catalogue. If nothing would be shown, the page is not changed.

    Args:
        title: A short label shown to the shopper, for example "Navy hoodies in M under $60" (at most 40 characters).
        query: Keywords for the kind of item, college, sport, or theme only. No sizes, colors, or prices.
        categories: Item types to show, for example ["Hoodies", "Quarter-Zips"]. Use the names from list_categories.
        sizes: Sizes the product must be in stock in (XS, S, M, L, XL, XXL).
        colors: Color families: Navy, Blue, Gray, White, Cream, Red, Black, Gold / Yellow, Green, Coral, Multicolor.
        min_price: Lowest price in US dollars.
        max_price: Highest price in US dollars.
        sort: How to order them if the shopper asked: relevance-desc, relevance-asc, price-desc, price-asc,
            name-asc, or name-desc.
    """
    results, showing, examples = build_page_results(title, query, categories, sizes, colors, min_price, max_price, sort)
    filters = clean_page_filters(categories, sizes, colors, min_price, max_price, sort)
    matches_before = results.total if results else len(find_products(query)[0])
    return PageShowing(
        title=title.strip(),
        matches_before_filters=matches_before,
        showing=showing if results else 0,
        filters=filters,
        examples=examples,
    )


def get_product_info(product_id: str) -> ProductInfo:
    """Look up one product's description, price, and stock, overall and for every size.

    Call this for any question about a product's price, what it is like, or how many are in stock.
    Every number comes straight from the Campus Customs database.

    Args:
        product_id: The product_id exactly as returned by search_products.
    """
    detail = product_detail(product_id)
    if detail is None:
        raise ModelRetry(f"No product has the id '{product_id}'. Use search_products to find valid product_ids.")
    sizes = [SizeAvailability(size=s.size, quantity=s.quantity, status=stock_status(s.quantity)) for s in detail.sizes]
    return ProductInfo(
        product_id=detail.product_id,
        name=detail.name,
        description=detail.description,
        colors=detail.colors,
        price=detail.price,
        price_display=format_price(detail.price),
        total_in_stock=sum(s.quantity for s in sizes),
        sizes=sizes,
        in_stock_sizes=[s.size for s in sizes if s.quantity > 0],
        sold_out_sizes=[s.size for s in sizes if s.quantity == 0],
    )


def check_stock(product_id: str, size: str) -> StockResult:
    """Check how many of one product are in stock in one size.

    Use this when the shopper asks about a specific size. The result says plainly if the size is sold out
    and lists the sizes that are still in stock.

    Args:
        product_id: The product_id exactly as returned by search_products.
        size: XS, S, M, L, XL, or XXL ("medium", "extra large", etc. also work).
    """
    canonical = normalize_size(size)
    if canonical is None:
        raise ModelRetry(f"'{size}' is not a size we carry. Valid sizes: {', '.join(SIZE_ORDER)}.")
    detail = product_detail(product_id)
    if detail is None:
        raise ModelRetry(f"No product has the id '{product_id}'. Use search_products to find valid product_ids.")
    quantity = next((s.quantity for s in detail.sizes if s.size == canonical), 0)
    return StockResult(
        product_id=product_id,
        name=detail.name,
        size=canonical,
        quantity=quantity,
        status=stock_status(quantity),
        other_sizes_in_stock=[s.size for s in detail.sizes if s.quantity > 0 and s.size != canonical],
    )


def list_categories() -> list[CategorySummary]:
    """List the kinds of apparel we sell, with how many products and the price range of each."""
    groups: dict[str, list[float]] = {}
    for product in all_products():
        groups.setdefault(category_of(product.garment_type), []).append(product.price)
    return [
        CategorySummary(category=name, product_count=len(prices), min_price=min(prices), max_price=max(prices))
        for name, prices in sorted(groups.items())
    ]


def get_customer_info(ctx: RunContext[ChatDeps]) -> CustomerProfile:
    """Get the name and email of the signed-in shopper you are chatting with.

    Use this when you need to know who they are, for example to greet them by name or when they ask what name or
    email is on their account. It only ever returns the shopper in this conversation. If nobody is signed in
    there is no profile, and you should invite them to log in or create an account.
    """
    if ctx.deps.customer is None:
        raise ModelRetry("Nobody is signed in, so there is no customer profile. Tell the shopper they can log in.")
    return ctx.deps.customer


# ---------------------------------------------------------------------------
# Page context (where the shopper is on the site)
# ---------------------------------------------------------------------------

PRODUCT_PATH = re.compile(r"^/products/([^/]+)/?$")


def resolve_page(page: ChatPage | None) -> PageContext | None:
    """Turn what the browser reports into trusted context. A product id is only used if it is a real product."""
    if page is None:
        return None
    path = page.path.split("?")[0].rstrip("/") or "/"
    match = PRODUCT_PATH.match(path)
    if match:
        product = next(iter(products_by_ids([match.group(1)])), None)
        if product:
            return PageContext(page="product", product_id=product.product_id, product_name=product.name)
        return PageContext(page="other")
    if path == "/":
        return PageContext(page="home")
    if path == "/products":
        return PageContext(page="products", showing_results=page.showing_results)
    if path == "/about":
        return PageContext(page="about")
    if path in ("/login", "/create-account"):
        return PageContext(page="account")
    return PageContext(page="other")


# ---------------------------------------------------------------------------
# Audit trail (output/audit_trail.json): one row per step of the agent loop
# ---------------------------------------------------------------------------

# AUDIT_TRAIL_PATH can point somewhere else (the tests do, so they never touch the real file).
AUDIT_TRAIL_PATH = Path(os.environ.get("AUDIT_TRAIL_PATH") or BACKEND_DIR.parent / "output" / "audit_trail.json")
AUDIT_TEXT_LIMIT = 120  # args and results are kept short on purpose
EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

audit_logger = logging.getLogger("campus_customs.audit")
audit_lock = threading.Lock()


def short_text(value: object, customer: CustomerProfile | None = None, limit: int = AUDIT_TEXT_LIMIT) -> str:
    """A one-line, length-capped version of any value. The repo is public, so shopper details are masked."""
    text = value if isinstance(value, str) else json.dumps(to_jsonable_python(value), ensure_ascii=False, separators=(",", ":"), default=str)
    text = " ".join(text.split())
    text = EMAIL_PATTERN.sub("[email]", text)
    if customer:
        for name in (customer.first_name, customer.last_name):
            if name:
                text = re.sub(re.escape(name), "[name]", text, flags=re.IGNORECASE)
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "\u2026"


def audit_entries(
    messages: list[ModelMessage],
    run_id: str,
    stop_reason: str,
    customer: CustomerProfile | None = None,
    detail: str | None = None,
) -> list[dict]:
    """Turn one chat turn's messages into audit rows: time, tool, short args, short result, stop reason.

    Every tool call is a row (stop reason "tool_call": the model stopped to use a tool). The call that delivered the
    final reply carries the turn's real stop reason. If the turn failed, one extra "agent_loop" row says why.
    """
    results: dict[str, ToolReturnPart | RetryPromptPart] = {}
    for message in messages:
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, (ToolReturnPart, RetryPromptPart)) and part.tool_call_id:
                    results[part.tool_call_id] = part

    entries: list[dict] = []
    for message in messages:
        if not isinstance(message, ModelResponse):
            continue
        when = message.timestamp.astimezone(timezone.utc).isoformat(timespec="seconds")
        for part in message.parts:
            if not isinstance(part, ToolCallPart):
                continue
            args = part.args_as_dict()
            outcome = results.get(part.tool_call_id)
            accepted = isinstance(outcome, ToolReturnPart)
            if part.tool_name == "final_result":
                shown_args = short_text({"product_ids": args.get("product_ids", [])}, customer)
                shown_result = short_text(args.get("message", ""), customer) if accepted else None
            else:
                shown_args = short_text(args, customer)
                shown_result = short_text(outcome.content, customer) if accepted else None
            if isinstance(outcome, RetryPromptPart):
                shown_result = "retry requested: " + short_text(outcome.content, customer, limit=AUDIT_TEXT_LIMIT - 17)
            if part.tool_name == "get_customer_info" and accepted:
                shown_result = "signed-in shopper's profile returned (name and email not logged)"
            entries.append(
                {
                    "time": when,
                    "run_id": run_id,
                    "tool": part.tool_name,
                    "args": shown_args,
                    "result": shown_result if shown_result is not None else "no result (the turn ended before this call finished)",
                    "stop_reason": "tool_call",
                }
            )

    if detail is None and entries and entries[-1]["tool"] == "final_result" and not entries[-1]["result"].startswith(("retry", "no result")):
        entries[-1]["stop_reason"] = stop_reason
    else:
        entries.append(
            {
                "time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "run_id": run_id,
                "tool": "agent_loop",
                "args": "",
                "result": short_text(detail or "the turn ended without a final reply", customer),
                "stop_reason": stop_reason,
            }
        )
    return entries


def append_audit_trail(entries: list[dict], path: Path | None = None) -> None:
    """Add rows to the end of the audit file. Earlier rows are never removed or rewritten.

    The file is a JSON list. If it can't be read as one, it is left alone (never overwritten) and the problem is
    logged. The new list is written to a temporary file first and swapped in, so a crash can't leave half a file.
    """
    if not entries:
        return
    target = path or AUDIT_TRAIL_PATH
    with audit_lock:
        existing: list = []
        if target.exists() and target.stat().st_size > 0:
            try:
                existing = json.loads(target.read_text(encoding="utf-8"))
                if not isinstance(existing, list):
                    raise ValueError("not a JSON list")
            except ValueError as error:
                audit_logger.error("Audit trail not updated: %s can't be read (%s). Fix or move it; nothing was overwritten.", target, error)
                return
        target.parent.mkdir(parents=True, exist_ok=True)
        handle, temp_name = tempfile.mkstemp(dir=target.parent, prefix=".audit_trail_", suffix=".tmp")
        try:
            with os.fdopen(handle, "w", encoding="utf-8") as temp:
                json.dump(existing + entries, temp, indent=2, ensure_ascii=False)
                temp.write("\n")
            os.replace(temp_name, target)
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise


def record_audit(
    messages: list[ModelMessage],
    run_id: str,
    stop_reason: str,
    customer: CustomerProfile | None = None,
    detail: str | None = None,
) -> None:
    """Write one chat turn to the audit trail. A problem here is logged but never breaks the chat."""
    try:
        append_audit_trail(audit_entries(messages, run_id, stop_reason, customer, detail))
    except Exception as error:
        audit_logger.error("Audit trail not updated: %s: %s", type(error).__name__, error)
