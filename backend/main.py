"""Campus Customs API: products, images, accounts, and the shop assistant chat.

Run from the backend/ folder, with the project's virtual environment active
(source ../.venv/bin/activate):
    uvicorn main:app --reload --port 8000
"""

import base64
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import sqlite3
import statistics
import time
from collections import defaultdict, deque
from functools import lru_cache
from io import BytesIO
from pathlib import Path

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from pydantic import BaseModel

# Secrets come from a .env file. hw4/.env is checked first (the simplest place after cloning), then the .env one
# folder above hw4/ (the class root). Values already in the environment win over both.
load_dotenv(Path(__file__).resolve().parents[1] / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from agent import AssistantUnavailable, respond  # noqa: E402  (after load_dotenv so the key is available)
from models import (  # noqa: E402
    ChatRequest,
    ChatResponse,
    CustomerProfile,
    HistoryMessage,
    Product,
    ProductCard,
    ProductDetail,
    StoredMessage,
)
from tools import DATA_DIR, DB_PATH, all_products, connect, product_detail, products_by_ids, resolve_page  # noqa: E402

IMAGES_DIR = DATA_DIR / "products"

if not DB_PATH.exists() or not IMAGES_DIR.is_dir():
    raise RuntimeError(f"Local data pack not found. Expected {DB_PATH} and {IMAGES_DIR}.")

# Many product photos have black bars baked in along the edges (a transparent
# background that was flattened to black). These settings detect those bars.
BAR_MAX_BRIGHTNESS = 45  # every colour channel in a bar line is at or below this
BAR_MAX_SPREAD = 12  # ...and the line is nearly uniform
MIN_BAR_PX = 3  # ignore anything thinner than this
EDGE_SAFETY_PX = 2  # also trim the soft JPEG edge next to a bar
SOLID_BLACK = 12  # a pixel this dark (every channel) is treated as pure black background
FILL_TOLERANCE = 24  # how far from pure black the flood fill is allowed to spread
FRINGE_PX = 2  # the dark anti-aliasing fringe around a garment is grown into the white background by this much
EDGE_SOFTEN_PX = 0.9  # ...and the new edge is softened by this much so it still looks smooth
POCKET_BLACK = 3  # black this pure (every channel) can only be background: garment shadows are never this flat
POCKET_MIN_WIDTH = 7  # ...and a gap between sleeve and body is at least this many pixels wide
MAX_POCKETS = 300  # safety limit on how many separate gaps are filled in one photo
LIGHT_BACKGROUND_MIN = 235  # an off-white background this light (every channel) is flattened to pure white
LIGHT_FILL_TOLERANCE = 30  # how far from the background colour the flood fill may spread

app = FastAPI(title="Campus Customs API")


@app.get("/api/products", response_model=list[Product])
def list_products() -> list[Product]:
    return all_products()


@app.get("/api/products/{product_id}", response_model=ProductDetail)
def get_product(product_id: str) -> ProductDetail:
    detail = product_detail(product_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return detail


# ---------------------------------------------------------------------------
# Accounts and login
# ---------------------------------------------------------------------------

# Passwords are hashed with Argon2id: deliberately slow and memory-hard, with a
# random salt generated per password and stored inside the hash string itself.
# 128 MiB of memory, 4 passes, 4 lanes: roughly 80 ms per hash on a laptop, which is
# negligible for one login but makes mass password guessing expensive.
hasher = PasswordHasher(time_cost=4, memory_cost=131072, parallelism=4)
# Verified when the email is unknown, so a login takes the same time either way.
DUMMY_HASH = hasher.hash("not-a-real-password")

SESSION_COOKIE = "cc_session"
SESSION_TTL_SECONDS = 7 * 24 * 60 * 60
SESSION_SECRET = os.environ.get("SESSION_SECRET") or ""
if not SESSION_SECRET:
    logging.getLogger("uvicorn.error").warning(
        "SESSION_SECRET is not set; using a random one, so logins reset when the server restarts."
    )
    SESSION_SECRET = secrets.token_hex(32)

# Accounts created before this login system store "pbkdf2_sha256$<salt>$<hex digest>"
# without the iteration count, so the common counts are tried. A legacy password is
# upgraded to Argon2id the first time its owner logs in successfully.
LEGACY_PREFIX = "pbkdf2_sha256$"
LEGACY_ITERATION_COUNTS = (600_000, 390_000, 310_000, 260_000, 210_000, 150_000, 120_000, 100_000, 50_000, 10_000, 1_000)
MAX_LOGIN_PASSWORD_LENGTH = 1024

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_NAME_LENGTH = 60
MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 10
MAX_PASSWORD_LENGTH = 128

# Login attempt limit: after this many failed logins for one account it is locked for a while,
# whether or not that email has an account (so the limit cannot be used to find out who is registered).
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCK_SECONDS = 15 * 60
# A looser limit per network address, to slow down guessing across many different emails.
LOGIN_IP_MAX_FAILURES = 30
failed_logins: dict[str, deque[float]] = defaultdict(deque)  # key -> times of recent failed logins


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    confirm_password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class User(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str


class AuthResponse(BaseModel):
    user: User | None
    password_update_required: bool = False  # True when the password they logged in with no longer meets the rules


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str


def verify_legacy_password(stored_hash: str, password: str) -> bool:
    try:
        _, salt, digest = stored_hash.split("$")
        expected = bytes.fromhex(digest)
    except ValueError:
        return False
    salts = [salt.encode()]  # the salt text itself, or its decoded bytes if it is hex / base64
    for decode in (bytes.fromhex, lambda v: base64.urlsafe_b64decode(v + "=" * (-len(v) % 4))):
        try:
            salts.append(decode(salt))
        except ValueError:
            pass
    for iterations in LEGACY_ITERATION_COUNTS:
        for salt_bytes in salts:
            candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_bytes, iterations)
            if hmac.compare_digest(candidate, expected):
                return True
    return False


def password_matches(row: sqlite3.Row | None, password: str) -> bool:
    """Check a password against a stored hash, in the same time whether or not the account exists."""
    stored_hash = row["password_hash"] if row else DUMMY_HASH
    if stored_hash.startswith(LEGACY_PREFIX):
        return verify_legacy_password(stored_hash, password)
    try:
        hasher.verify(stored_hash, password)
        return row is not None
    except (VerificationError, InvalidHashError):  # wrong password, or an unsupported hash format
        return False


def connect_for_write() -> sqlite3.Connection:
    # Only the accounts code writes to the database (new rows in `users`).
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def to_user(row: sqlite3.Row) -> User:
    name_parts = row["name"].split(" ", 1)
    return User(
        id=row["id"],
        first_name=row["first_name"] or name_parts[0],
        last_name=row["last_name"] or (name_parts[1] if len(name_parts) > 1 else ""),
        email=row["email"],
    )


def sign(payload: str) -> str:
    return hmac.new(SESSION_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_session_token(user_id: int, needs_password_update: bool = False) -> str:
    # The flag rides in the signed cookie, so it cannot be changed by the browser.
    payload = f"{user_id}.{int(time.time()) + SESSION_TTL_SECONDS}.{int(needs_password_update)}"
    return f"{payload}.{sign(payload)}"


def read_session_token(token: str | None) -> tuple[int, bool] | None:
    """The signed-in user id and whether they still need to update their password, or None if invalid."""
    try:
        user_id, expires, flag, signature = (token or "").split(".")
        if not hmac.compare_digest(signature, sign(f"{user_id}.{expires}.{flag}")) or int(expires) < time.time():
            return None
        return int(user_id), flag == "1"
    except ValueError:
        return None


def start_session(response: Response, user_id: int, needs_password_update: bool = False) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        make_session_token(user_id, needs_password_update),
        max_age=SESSION_TTL_SECONDS,
        httponly=True,  # not readable from JavaScript
        samesite="lax",
        secure=False,  # set to True when the site is served over HTTPS
        path="/",
    )


def bad_request(message: str) -> HTTPException:
    return HTTPException(status_code=400, detail=message)


def normalize_email(email: str) -> str:
    email = email.strip().lower()
    if len(email) > MAX_EMAIL_LENGTH or not EMAIL_PATTERN.match(email):
        raise bad_request("Please enter a valid email address.")
    return email


def password_problems(password: str) -> list[str]:
    """What a new password is missing. Empty means it meets the rules: at least 10 characters,
    with a letter, a number, and a special character (anything that is not a letter, digit, or space)."""
    problems = []
    if len(password) < MIN_PASSWORD_LENGTH:
        problems.append(f"be at least {MIN_PASSWORD_LENGTH} characters")
    if not any(c.isalpha() for c in password):
        problems.append("include a letter")
    if not any(c.isdigit() for c in password):
        problems.append("include a number")
    if not any(not c.isalnum() and not c.isspace() for c in password):
        problems.append("include a special character (like ! ? # $ %)")
    return problems


def join_requirements(problems: list[str]) -> str:
    return problems[0] if len(problems) == 1 else ", ".join(problems[:-1]) + (", and " if len(problems) > 2 else " and ") + problems[-1]


def lock_seconds_left(key: str, max_failures: int) -> int:
    """Seconds until `key` may try to log in again, or 0 if it is not locked."""
    now = time.time()
    failures = failed_logins.get(key)
    if failures is None:
        return 0
    while failures and failures[0] < now - LOGIN_LOCK_SECONDS:
        failures.popleft()
    if not failures:
        del failed_logins[key]
        return 0
    if len(failures) >= max_failures:
        return max(1, int(failures[-1] + LOGIN_LOCK_SECONDS - now) + 1)
    return 0


def record_failed_login(*keys: str) -> None:
    now = time.time()
    if len(failed_logins) > 10_000:  # keep memory bounded: forget keys whose failures have all expired
        for key in [k for k, f in failed_logins.items() if not f or f[-1] < now - LOGIN_LOCK_SECONDS]:
            del failed_logins[key]
    for key in keys:
        failed_logins[key].append(now)


def locked_out(seconds: int) -> HTTPException:
    minutes = -(-seconds // 60)
    return HTTPException(
        status_code=429,
        detail=f"Too many failed login attempts. Please try again in {minutes} minute{'s' if minutes != 1 else ''}.",
        headers={"Retry-After": str(seconds)},
    )


@app.post("/api/auth/register", response_model=AuthResponse, status_code=201)
def register(body: RegisterRequest, response: Response) -> AuthResponse:
    first, last = body.first_name.strip(), body.last_name.strip()
    if not first or not last:
        raise bad_request("Please enter your first and last name.")
    if len(first) > MAX_NAME_LENGTH or len(last) > MAX_NAME_LENGTH:
        raise bad_request(f"Names can be at most {MAX_NAME_LENGTH} characters.")
    email = normalize_email(body.email)
    if len(body.password) > MAX_PASSWORD_LENGTH:
        raise bad_request(f"Password can be at most {MAX_PASSWORD_LENGTH} characters.")
    problems = password_problems(body.password)
    if problems:
        raise bad_request(f"Password must {join_requirements(problems)}.")
    if body.password != body.confirm_password:
        raise bad_request("Passwords do not match.")

    password_hash = hasher.hash(body.password)  # random salt included
    try:
        with connect_for_write() as conn:
            if conn.execute("SELECT 1 FROM users WHERE lower(email) = ?", (email,)).fetchone():
                raise HTTPException(status_code=409, detail="An account with that email already exists.")
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash, first_name, last_name) VALUES (?, ?, ?, ?, ?)",
                (f"{first} {last}", email, password_hash, first, last),
            )
            row = conn.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    except sqlite3.IntegrityError:  # two sign-ups with the same email at once
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    start_session(response, row["id"])
    return AuthResponse(user=to_user(row))


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest, request: Request, response: Response) -> AuthResponse:
    email = body.email.strip().lower()
    email_key = f"email:{email}"
    ip_key = f"ip:{request.client.host if request.client else 'unknown'}"

    wait = max(lock_seconds_left(email_key, LOGIN_MAX_ATTEMPTS), lock_seconds_left(ip_key, LOGIN_IP_MAX_FAILURES))
    if wait:
        raise locked_out(wait)  # locked: the password is not even checked

    def failed() -> HTTPException:
        record_failed_login(email_key, ip_key)
        attempts_left = LOGIN_MAX_ATTEMPTS - len(failed_logins[email_key])
        if attempts_left <= 0:
            return locked_out(LOGIN_LOCK_SECONDS)
        return HTTPException(
            status_code=401,
            detail=f"Incorrect email or password. You have {attempts_left} attempt{'s' if attempts_left != 1 else ''} left.",
        )

    if len(body.password) > MAX_LOGIN_PASSWORD_LENGTH:
        raise failed()
    with connect_for_write() as conn:
        row = conn.execute("SELECT * FROM users WHERE lower(email) = ?", (email,)).fetchone()
        if not password_matches(row, body.password):
            raise failed()
        if row["password_hash"].startswith(LEGACY_PREFIX) or hasher.check_needs_rehash(row["password_hash"]):
            # move to the current Argon2id settings
            conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hasher.hash(body.password), row["id"]))
    failed_logins.pop(email_key, None)  # a successful login clears this account's failed attempts
    # This is the only moment the server sees the plain password, so it is the moment to check it against
    # the current rules. A password that falls short means the shopper is asked to update it.
    needs_update = bool(password_problems(body.password))
    start_session(response, row["id"], needs_update)
    return AuthResponse(user=to_user(row), password_update_required=needs_update)


@app.post("/api/auth/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/")


def signed_in_user(request: Request) -> sqlite3.Row | None:
    session = read_session_token(request.cookies.get(SESSION_COOKIE))
    if session is None:
        return None
    with connect() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (session[0],)).fetchone()


@app.get("/api/auth/me", response_model=AuthResponse)
def current_user(request: Request) -> AuthResponse:
    row = signed_in_user(request)
    session = read_session_token(request.cookies.get(SESSION_COOKIE))
    return AuthResponse(user=to_user(row) if row else None, password_update_required=bool(row and session and session[1]))


@app.post("/api/auth/change-password", response_model=AuthResponse)
def change_password(body: ChangePasswordRequest, request: Request, response: Response) -> AuthResponse:
    user = signed_in_user(request)
    if user is None:
        raise HTTPException(status_code=401, detail="Please log in first.")
    email_key = f"email:{user['email'].lower()}"
    wait = lock_seconds_left(email_key, LOGIN_MAX_ATTEMPTS)
    if wait:
        raise locked_out(wait)  # the same limit as logging in, so this cannot be used to guess the password
    if len(body.current_password) > MAX_LOGIN_PASSWORD_LENGTH or not password_matches(user, body.current_password):
        record_failed_login(email_key)
        attempts_left = LOGIN_MAX_ATTEMPTS - len(failed_logins[email_key])
        if attempts_left <= 0:
            raise locked_out(LOGIN_LOCK_SECONDS)
        raise HTTPException(
            status_code=401,
            detail=f"Your current password is incorrect. You have {attempts_left} attempt{'s' if attempts_left != 1 else ''} left.",
        )
    if len(body.new_password) > MAX_PASSWORD_LENGTH:
        raise bad_request(f"Password can be at most {MAX_PASSWORD_LENGTH} characters.")
    problems = password_problems(body.new_password)
    if problems:
        raise bad_request(f"Password must {join_requirements(problems)}.")
    if body.new_password != body.confirm_password:
        raise bad_request("Passwords do not match.")
    if body.new_password == body.current_password:
        raise bad_request("Please choose a new password that is different from your current one.")
    with connect_for_write() as conn:
        conn.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hasher.hash(body.new_password), user["id"]))
    failed_logins.pop(email_key, None)
    start_session(response, user["id"], needs_password_update=False)
    return AuthResponse(user=to_user(user), password_update_required=False)


# ---------------------------------------------------------------------------
# Shop assistant chat
# ---------------------------------------------------------------------------

MAX_MESSAGE_LENGTH = 1000
MAX_HISTORY_MESSAGES = 12  # earlier turns sent along for context
MAX_HISTORY_CONTENT = 2000
STORED_HISTORY_LIMIT = 50
CHAT_LIMIT = 20  # messages allowed per person...
CHAT_WINDOW_SECONDS = 600  # ...in this many seconds (each message costs a model call)
chat_calls: dict[str, deque[float]] = defaultdict(deque)
chat_logger = logging.getLogger("uvicorn.error")


def check_chat_rate_limit(key: str) -> None:
    now = time.time()
    calls = chat_calls[key]
    while calls and calls[0] < now - CHAT_WINDOW_SECONDS:
        calls.popleft()
    if len(calls) >= CHAT_LIMIT:
        raise HTTPException(status_code=429, detail="You're sending messages quickly. Please wait a few minutes and try again.")
    calls.append(now)


def recent_history(user_id: int) -> list[HistoryMessage]:
    """A signed-in shopper's latest saved messages, oldest first. This is the agent's memory of them."""
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM (SELECT id, role, content FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id",
            (user_id, MAX_HISTORY_MESSAGES),
        ).fetchall()
    return [HistoryMessage(role=r["role"], content=r["content"][:MAX_HISTORY_CONTENT]) for r in rows]


def save_chat_turn(user_id: int, message: str, reply: ChatResponse) -> None:
    products_json = json.dumps([p.model_dump() for p in reply.products]) if reply.products else None  # product cards
    with connect_for_write() as conn:
        conn.execute("INSERT INTO chat_messages (user_id, role, content) VALUES (?, 'user', ?)", (user_id, message))
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) VALUES (?, 'assistant', ?, ?)",
            (user_id, reply.message, products_json),
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    message = body.message.strip()
    if not message:
        raise bad_request("Please type a message.")
    if len(message) > MAX_MESSAGE_LENGTH:
        raise bad_request(f"Messages can be at most {MAX_MESSAGE_LENGTH} characters.")
    user = signed_in_user(request)
    check_chat_rate_limit(f"user:{user['id']}" if user else f"ip:{request.client.host if request.client else 'unknown'}")
    if user:
        # Signed in: the agent remembers them from the database, not from whatever the browser sends.
        history = recent_history(user["id"])
        profile = to_user(user)
        customer = CustomerProfile(first_name=profile.first_name, last_name=profile.last_name, email=profile.email)
    else:
        history = [
            HistoryMessage(role=m.role, content=m.content[:MAX_HISTORY_CONTENT]) for m in body.history[-MAX_HISTORY_MESSAGES:]
        ]
        customer = None
    try:
        reply = await respond(message, history, customer=customer, page=resolve_page(body.page))
    except AssistantUnavailable as error:
        chat_logger.error("Assistant unavailable: %s", error)
        raise HTTPException(status_code=503, detail="The assistant isn't available right now.")
    except Exception as error:  # model/network failures; details go to the server log, never the browser
        chat_logger.error("Assistant call failed: %s: %s", type(error).__name__, error)
        raise HTTPException(status_code=502, detail="The assistant couldn't answer just now. Please try again in a moment.")
    if user:
        save_chat_turn(user["id"], message, reply)
    return reply


@app.get("/api/chat/history", response_model=list[StoredMessage])
def chat_history(request: Request) -> list[StoredMessage]:
    user = signed_in_user(request)
    if user is None:
        return []
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM (SELECT * FROM chat_messages WHERE user_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id",
            (user["id"], STORED_HISTORY_LIMIT),
        ).fetchall()
    messages = []
    for row in rows:
        ids = [p["product_id"] for p in json.loads(row["products_json"])] if row["products_json"] else []
        cards = [ProductCard.from_product(p) for p in products_by_ids(ids)]
        messages.append(StoredMessage(role=row["role"], content=row["content"], products=cards))
    return messages


def bar_width(img: Image.Image, side: str) -> int:
    """Number of consecutive black edge lines on one side ("L", "R", "T" or "B")."""
    w, h = img.size
    limit = (w if side in "LR" else h) // 3
    count = 0
    while count < limit:
        k = count
        box = {"L": (k, 0, k + 1, h), "R": (w - 1 - k, 0, w - k, h), "T": (0, k, w, k + 1), "B": (0, h - 1 - k, w, h - k)}[side]
        if not all(hi <= BAR_MAX_BRIGHTNESS and hi - lo <= BAR_MAX_SPREAD for lo, hi in img.crop(box).getextrema()):
            break
        count += 1
    return count


def edge_color(img: Image.Image) -> tuple[int, int, int]:
    """The photo's own background colour: the median colour around its border."""
    w, h = img.size
    px = img.load()
    edge = [px[x, 0] for x in range(w)] + [px[x, h - 1] for x in range(w)]
    edge += [px[0, y] for y in range(h)] + [px[w - 1, y] for y in range(h)]
    return tuple(int(statistics.median(p[c] for p in edge)) for c in range(3))


def border_points(img: Image.Image, step: int = 16) -> list[tuple[int, int]]:
    """Points along the photo's border, used as starting points for filling the background.

    Spaced out so a background pocket that the corners cannot reach (for example behind a sleeve
    that touches the edge) still gets filled. A point already filled costs almost nothing.
    """
    w, h = img.size
    xs = list(range(0, w, step)) + [w - 1]
    ys = list(range(0, h, step)) + [h - 1]
    return [(x, 0) for x in xs] + [(x, h - 1) for x in xs] + [(0, y) for y in ys] + [(w - 1, y) for y in ys]


def enclosed_black_pockets(img: Image.Image, outside: Image.Image) -> Image.Image:
    """Mask of background that is boxed in by the garment, like the gap between a sleeve and the body.

    These gaps are not connected to the photo's border, so the border fill never reaches them. Only
    pixels that are essentially pure black (garment shadows are never that flat) in areas wide enough
    to be a real gap count, so black details and dark navy shading are left alone.
    """
    r, g, b = img.split()
    black = ImageChops.darker(ImageChops.darker(r, g), b).point(lambda v: 255 if v <= POCKET_BLACK else 0)
    candidates = ImageChops.subtract(black, outside)
    cores = candidates.filter(ImageFilter.MinFilter(POCKET_MIN_WIDTH))  # only wide-enough areas survive
    pockets = candidates.copy()
    width = img.size[0]
    for _ in range(MAX_POCKETS):
        position = cores.tobytes().find(b"\xff")
        if position == -1:
            break
        seed = (position % width, position // width)
        ImageDraw.floodfill(pockets, seed, 128, thresh=0)  # mark the whole gap this core belongs to
        ImageDraw.floodfill(cores, seed, 0, thresh=0)  # and take it off the list
    return pockets.point(lambda v: 255 if v == 128 else 0)


def whiten_black_background(img: Image.Image) -> Image.Image:
    """Turn the black background (a flattened transparent PNG) into white.

    This covers the background around the garment and the gaps boxed in by it (between the sleeves and
    the body). Black details inside the garment are kept. The dark fringe left around every outline is
    absorbed into the white, and the new edge is softened, so the garment looks like it is floating.
    """
    marker = (255, 0, 255)
    filled = img.copy()
    for seed in border_points(img):
        if max(filled.getpixel(seed)) <= SOLID_BLACK:
            ImageDraw.floodfill(filled, seed, marker, thresh=FILL_TOLERANCE)
    r, g, b = filled.split()
    background = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v >= 250 else 0), g.point(lambda v: 255 if v <= 5 else 0)), b.point(lambda v: 255 if v >= 250 else 0))
    background = ImageChops.lighter(background, enclosed_black_pockets(img, background))
    grown = background.filter(ImageFilter.MaxFilter(2 * FRINGE_PX + 1))
    alpha = grown.filter(ImageFilter.GaussianBlur(EDGE_SOFTEN_PX))  # 255 where the photo should become white
    return Image.composite(Image.new("RGB", img.size, (255, 255, 255)), img, alpha)


def flatten_light_background(img: Image.Image) -> Image.Image:
    """Turn an off-white background (for example 250 instead of 255) into pure white, so there is no faint box."""
    # Fill with a colour that is nowhere near white: the fill stops immediately if its colour is within
    # the tolerance of the start pixel, which is the case for white on an off-white background.
    marker = (255, 0, 255)
    filled = img.copy()
    for seed in border_points(img):
        if min(filled.getpixel(seed)) >= LIGHT_BACKGROUND_MIN:
            ImageDraw.floodfill(filled, seed, marker, thresh=LIGHT_FILL_TOLERANCE)
    r, g, b = filled.split()
    background = ImageChops.multiply(ImageChops.multiply(r.point(lambda v: 255 if v >= 250 else 0), g.point(lambda v: 255 if v <= 5 else 0)), b.point(lambda v: 255 if v >= 250 else 0))
    return Image.composite(Image.new("RGB", img.size, (255, 255, 255)), img, background)


@lru_cache(maxsize=None)
def cleaned_image(filename: str) -> bytes | None:
    """JPEG bytes with baked-in black bars and non-white backgrounds cleaned up, or None.

    Bars are cropped off and the photo is padded back out to a square in its own
    background colour so the product stays centred. If that background is black
    (a flattened transparent PNG) or off-white, it is turned pure white so every
    photo looks like it floats on the white page.
    """
    img = Image.open(IMAGES_DIR / filename).convert("RGB")
    left, right, top, bottom = (bar_width(img, side) for side in "LRTB")
    has_bars = max(left, right, top, bottom) >= MIN_BAR_PX
    trim = lambda n: n + EDGE_SAFETY_PX if n and has_bars else 0
    w, h = img.size
    crop = img.crop((trim(left), trim(top), w - trim(right), h - trim(bottom)))
    background = edge_color(crop)
    black_background = max(background) <= SOLID_BLACK
    light_background = LIGHT_BACKGROUND_MIN <= min(background) < 253  # off-white, not already pure white
    if not has_bars and not black_background and not light_background:
        return None
    side = max(crop.size)
    canvas = Image.new("RGB", (side, side), background)
    canvas.paste(crop, ((side - crop.width) // 2, (side - crop.height) // 2))
    if black_background:
        canvas = whiten_black_background(canvas)
    elif light_background:
        canvas = flatten_light_background(canvas)
    out = BytesIO()
    canvas.save(out, "JPEG", quality=90)
    return out.getvalue()


# Image URLs carry a version (see IMAGE_VERSION in tools.py), so a changed photo gets a new URL
# and browsers can safely keep each version for a day.
IMAGE_CACHE_HEADERS = {"Cache-Control": "public, max-age=86400"}


@app.get("/images/{filename}")
def get_image(filename: str):
    # Serves only files inside data/products/, so the database file is never exposed.
    path = IMAGES_DIR / Path(filename).name
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Image not found")
    cleaned = cleaned_image(path.name)
    if cleaned is None:
        return FileResponse(path, headers=IMAGE_CACHE_HEADERS)
    return Response(cleaned, media_type="image/jpeg", headers=IMAGE_CACHE_HEADERS)
