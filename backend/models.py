"""Structured types shared by the API and the shop assistant (PydanticAI agent)."""

from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel, Field

# ---- Catalogue ----


class Product(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    image_url: str
    # Used by the Products page filters.
    category: str = Field(default="", description="Item type, e.g. Hoodies or Quarter-Zips.")
    primary_color: str = Field(
        default="",
        description="The one color family the Color filter uses for this item, e.g. Navy. `colors` still lists every color.",
    )
    available_sizes: list[str] = Field(default_factory=list, description="Sizes currently in stock, XS to XXL.")


class SizeStock(BaseModel):
    size: str
    quantity: int


class ProductDetail(Product):
    sizes: list[SizeStock]


class ProductCard(BaseModel):
    """What the website shows for a product in chat results: a photo, name, price, and one line of short info."""

    product_id: str
    name: str
    price: float
    image_url: str
    short_info: str = Field(description="One short line, e.g. 'Short-sleeve T-shirt · heather gray, white'.")

    @classmethod
    def from_product(cls, product: Product) -> "ProductCard":
        kind = product.garment_type[:1].upper() + product.garment_type[1:]
        colors = ", ".join(product.colors[:2])
        return cls(
            product_id=product.product_id,
            name=product.name,
            price=product.price,
            image_url=product.image_url,
            short_info=f"{kind} · {colors}" if colors else kind,
        )


SortKey = Literal["relevance-desc", "relevance-asc", "price-desc", "price-asc", "name-asc", "name-desc"]


class PageFilters(BaseModel):
    """Filters (and a sort order) the assistant turns on for the shopper on the Products page.

    The shopper sees them switched on in the filter panel and can change or clear them.
    """

    categories: list[str] = Field(default_factory=list, description="Item types, e.g. Hoodies.")
    sizes: list[str] = Field(default_factory=list, description="Sizes the product must be in stock in, XS to XXL.")
    colors: list[str] = Field(default_factory=list, description="Color families, e.g. Navy.")
    min_price: float | None = None
    max_price: float | None = None
    sort: SortKey | None = None

    def is_empty(self) -> bool:
        return not (self.categories or self.sizes or self.colors or self.min_price is not None or self.max_price is not None or self.sort)


class SearchResults(BaseModel):
    """What the website shows on the Products page after the assistant searches: a set of products plus the
    filters the assistant turned on for them."""

    title: str = Field(description="Short label for the search, e.g. 'T-shirts'.")
    total: int = Field(description="How many products there are before the filters are applied.")
    products: list[ProductCard]
    filters: PageFilters | None = Field(default=None, description="Filters to switch on, if the request needed any.")


# ---- What the agent's tools return (all values come straight from the database) ----

StockStatus = Literal["in stock", "low stock", "sold out"]


class ProductResult(BaseModel):
    """A search hit: price and description, plus which sizes are in stock and which are sold out."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str]
    price: float
    price_display: str = Field(description="The price formatted for the shopper, e.g. $72.00. Quote this.")
    available_sizes: list[str]
    sold_out_sizes: list[str]
    requested_size: str | None = Field(default=None, description="The size the search asked about, if any.")
    requested_size_in_stock: bool | None = Field(
        default=None, description="Whether the requested size is in stock. False means it is sold out."
    )


class SearchResponse(BaseModel):
    """What search_products returns: the best matches plus how many products matched in total."""

    total_matches: int = Field(
        description="How many products in the whole catalogue matched. `results` shows only the best few."
    )
    results: list[ProductResult]


class PageShowing(BaseModel):
    """What show_on_page returns: what the shopper's page now shows, so the assistant can describe it accurately."""

    title: str
    matches_before_filters: int = Field(description="Products that matched the item keywords, before any filters.")
    showing: int = Field(description="Products the page shows after the filters are applied.")
    filters: PageFilters
    examples: list[str] = Field(description="A few of the products shown, with prices.")


class SizeAvailability(BaseModel):
    """Stock for one size of one product."""

    size: str
    quantity: int
    status: StockStatus


class ProductInfo(BaseModel):
    """Everything the assistant may say about one product: description, price, and stock overall and by size."""

    product_id: str
    name: str
    description: str
    colors: list[str] = Field(description="Colors from the catalogue. May be empty if none are listed.")
    price: float
    price_display: str = Field(description="The price formatted for the shopper, e.g. $72.00. Quote this.")
    total_in_stock: int
    sizes: list[SizeAvailability]
    in_stock_sizes: list[str]
    sold_out_sizes: list[str]


class StockResult(BaseModel):
    """Stock for one product in one size, with the sizes that could be offered instead."""

    product_id: str
    name: str
    size: str
    quantity: int
    status: StockStatus
    other_sizes_in_stock: list[str]


class CategorySummary(BaseModel):
    category: str
    product_count: int
    min_price: float
    max_price: float


# ---- The agent itself ----


class CustomerProfile(BaseModel):
    """Who is chatting. Only the signed-in shopper's own details, never anyone else's."""

    first_name: str
    last_name: str
    email: str


class PageContext(BaseModel):
    """Where the shopper is on the site, checked by the server, so the agent knows what "this" means."""

    page: Literal["home", "products", "product", "about", "account", "other"]
    product_id: str | None = Field(default=None, description="Set on a product page: the item the shopper is viewing.")
    product_name: str | None = Field(default=None, description="Looked up from the database, never taken from the browser.")
    showing_results: bool = Field(
        default=False, description="True when the Products page is showing the assistant's search results."
    )


@dataclass
class ChatDeps:
    """Per-conversation context passed to the agent: who is chatting (None for guests) and where they are on the site."""

    customer: CustomerProfile | None = None
    page: PageContext | None = None


class AgentReply(BaseModel):
    """What the agent must return for every turn."""

    message: str = Field(
        description="The reply shown to the shopper: friendly, concise, plain text with no markdown."
    )
    product_ids: list[str] = Field(
        default_factory=list,
        max_length=6,
        description=(
            "product_ids (exactly as returned by the tools) to show as small product cards under the message. "
            "Leave empty when no specific products are being recommended."
        ),
    )


# ---- Chat API ----


class HistoryMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatPage(BaseModel):
    """What the browser says about the current page. The server checks it before the agent sees it."""

    path: str
    showing_results: bool = False


class ChatRequest(BaseModel):
    message: str
    history: list[HistoryMessage] = Field(
        default_factory=list, description="Earlier messages. Used for guests; signed-in shoppers' history comes from the database."
    )
    page: ChatPage | None = None


class ChatResponse(BaseModel):
    """A reply returned to the website: the assistant's text plus any product cards to show under it."""

    message: str
    products: list[ProductCard] = Field(default_factory=list)
    results: SearchResults | None = Field(
        default=None, description="Present when the website should show a set of search results as cards on the page."
    )


class StoredMessage(BaseModel):
    """One saved chat message, restored for a signed-in shopper."""

    role: Literal["user", "assistant"]
    content: str
    products: list[ProductCard] = Field(default_factory=list)
