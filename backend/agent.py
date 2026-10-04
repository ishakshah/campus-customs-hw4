"""The Campus Customs shop assistant: a PydanticAI agent that calls OpenAI through Portkey."""

import os
import re
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")  # keep the startup banner out of the server log

from openai import AsyncOpenAI  # noqa: E402
from pydantic_ai import Agent, ModelRetry, RunContext, capture_run_messages  # noqa: E402
from pydantic_ai.exceptions import ModelHTTPError, UnexpectedModelBehavior  # noqa: E402
from pydantic_ai.messages import (  # noqa: E402
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.openai import OpenAIChatModel  # noqa: E402
from pydantic_ai.providers.openai import OpenAIProvider  # noqa: E402
from pydantic_ai.usage import UsageLimits  # noqa: E402
from pydantic_core import to_jsonable_python  # noqa: E402

from models import (  # noqa: E402
    AgentReply,
    ChatDeps,
    ChatResponse,
    CustomerProfile,
    HistoryMessage,
    PageContext,
    ProductCard,
    SearchResults,
)
from tools import (  # noqa: E402
    build_page_results,
    check_stock,
    get_customer_info,
    get_product_info,
    list_categories,
    products_by_ids,
    record_audit,
    search_products,
    show_on_page,
)

# Default model for the assistant. Do not swap in another model without asking the project owner.
MODEL_NAME = "gpt-5.6-luna"
PORTKEY_BASE_URL = "https://api.portkey.ai/v1"
PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "prompt.md"

MAX_MODEL_REQUESTS = 8  # per chat turn, including tool-calling round trips
MAX_PRODUCT_CARDS = 4  # small cards shown under one chat reply
REQUEST_TIMEOUT_SECONDS = 60


FILTERED_REPLY = (
    "I can only help with Campus Customs products, sizes, colors, prices, and availability. "
    "Is there something in our Yale apparel I can help you find?"
)


UNVERIFIED_REPLY = (
    "I couldn't confirm those details just now. Could you tell me which product and size you mean, and I'll look it up again?"
)


class AssistantUnavailable(Exception):
    """The assistant cannot run, for example because the Portkey key is missing."""


# ---------------------------------------------------------------------------
# Grounding: prices and quantities in a reply must come from the database
# ---------------------------------------------------------------------------

PRICE_PATTERN = re.compile(r"\$\s?(\d[\d,]*(?:\.\d+)?)")
QUANTITY_PATTERNS = (
    re.compile(r"\b(\d+)\s+(?:units?\s+|pieces?\s+)?(?:left|remaining|in stock)\b", re.IGNORECASE),  # "5 left"
    re.compile(r"\b(\d+)\s+(?:units?|pieces?)\b", re.IGNORECASE),  # "12 units"
    re.compile(r"\b(?:total of|in total)\s+(\d+)\b", re.IGNORECASE),  # "a total of 51"
)
SIZE_COUNT_PATTERNS = (  # (size, count) pairs: "M: 5", "M (5)", "M has 5"
    re.compile(r"\b(XS|S|M|L|XL|XXL)\s*[:=(\-\u2013]\s*(\d+)\b"),
    re.compile(r"\b(XS|S|M|L|XL|XXL)\s+(?i:has|have|with)\s+(\d+)\b"),
)
COUNT_THEN_SIZE = re.compile(r"\b(\d+)\s+(?:in\s+)?(?:size\s+)?(XS|S|M|L|XL|XXL)\b")  # "5 in M"
STOCK_CLAIM = re.compile(r"\b(?:in stock|sold out|out of stock|available in|only \d+ left)\b", re.IGNORECASE)


@dataclass
class ToolFacts:
    """Every price and quantity the tools returned during this turn."""

    prices: set[float] = field(default_factory=set)
    quantities: set[int] = field(default_factory=set)
    size_counts: set[tuple[str, int]] = field(default_factory=set)
    used_tools: bool = False


def collect_tool_facts(messages: list[ModelMessage]) -> ToolFacts:
    facts = ToolFacts()

    def walk(node: object) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            for key in ("price", "min_price", "max_price"):
                if isinstance(node.get(key), (int, float)):
                    facts.prices.add(round(float(node[key]), 2))
            if isinstance(node.get("total_in_stock"), int):
                facts.quantities.add(node["total_in_stock"])
            if isinstance(node.get("quantity"), int):
                facts.quantities.add(node["quantity"])
                if isinstance(node.get("size"), str):
                    facts.size_counts.add((node["size"], node["quantity"]))
            for value in node.values():
                walk(value)

    for message in messages:
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, ToolReturnPart):
                    facts.used_tools = True
                    walk(to_jsonable_python(part.content))
    return facts


def numbers_the_shopper_typed(messages: list[ModelMessage]) -> set[float]:
    """Numbers in the shopper's own messages (a budget like "under $75") may be repeated back."""
    numbers: set[float] = set()
    for message in messages:
        if isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, UserPromptPart) and isinstance(part.content, str):
                    numbers.update(float(n.replace(",", "")) for n in re.findall(r"\d[\d,]*(?:\.\d+)?", part.content))
    return numbers


def check_grounding(message: str, messages: list[ModelMessage]) -> list[str]:
    """Problems with a draft reply: prices or stock numbers the database tools did not return."""
    prices = [float(p.replace(",", "")) for p in PRICE_PATTERN.findall(message)]
    quantities = [int(q) for pattern in QUANTITY_PATTERNS for q in pattern.findall(message)]
    size_counts = [(size, int(n)) for pattern in SIZE_COUNT_PATTERNS for size, n in pattern.findall(message)]
    size_counts += [(size, int(n)) for n, size in COUNT_THEN_SIZE.findall(message)]
    claims_stock = bool(STOCK_CLAIM.search(message))

    facts = collect_tool_facts(messages)
    if (prices or quantities or size_counts or claims_stock) and not facts.used_tools:
        return [
            "You gave a price or stock details without looking them up. Call search_products, get_product_info, "
            "or check_stock first, then answer using only what they return."
        ]
    typed = numbers_the_shopper_typed(messages)
    problems = []
    for price in prices:
        if price not in typed and not any(abs(price - known) < 0.01 for known in facts.prices):
            problems.append(f"${price:g} is not a price returned by your tools. Quote prices exactly as the tools give them.")
    for quantity in quantities:
        if quantity not in facts.quantities and quantity not in typed:
            problems.append(f"The quantity {quantity} was not returned by your tools. Quote stock numbers exactly as the tools give them.")
    for size, count in size_counts:
        if (size, count) not in facts.size_counts and count not in typed:
            problems.append(f"Size {size} with {count} in stock does not match your tool results. Quote stock by size exactly as the tools give it.")
    return problems


def last_tool_arguments(messages: list[ModelMessage], tool_name: str) -> dict | None:
    """The arguments of the most recent successful call to `tool_name` in this turn, if there was one."""
    calls: dict[str, dict] = {}
    last: dict | None = None
    for message in messages:
        if isinstance(message, ModelResponse):
            for part in message.parts:
                if isinstance(part, ToolCallPart) and part.tool_name == tool_name:
                    calls[part.tool_call_id] = part.args_as_dict()
        elif isinstance(message, ModelRequest):
            for part in message.parts:
                if isinstance(part, ToolReturnPart) and part.tool_name == tool_name and part.tool_call_id in calls:
                    last = calls[part.tool_call_id]
    return last


@lru_cache(maxsize=1)
def get_agent() -> Agent[ChatDeps, AgentReply]:
    api_key = os.environ.get("PORTKEY_API_KEY")
    if not api_key:
        raise AssistantUnavailable("PORTKEY_API_KEY is not set in the .env file.")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-api-key": api_key},
    )
    model = OpenAIChatModel(MODEL_NAME, provider=OpenAIProvider(openai_client=client))
    agent = Agent(
        model,
        deps_type=ChatDeps,
        output_type=AgentReply,
        tools=[search_products, show_on_page, get_product_info, check_stock, list_categories, get_customer_info],
        retries=2,
    )

    @agent.instructions
    def system_prompt() -> str:
        # Read on every turn, so edits to prompts/prompt.md apply without restarting.
        return PROMPT_PATH.read_text()

    @agent.instructions
    def conversation_context(ctx: RunContext[ChatDeps]) -> str:
        """Who is chatting and where they are on the site. Only values the server has checked go in here."""
        lines = []
        customer = ctx.deps.customer
        if customer:
            lines.append(
                f"The shopper is signed in. Their name is {customer.first_name} {customer.last_name}. "
                "Call get_customer_info if you need their email."
            )
        else:
            lines.append("The shopper is not signed in (a guest).")
        page = ctx.deps.page
        if page and page.page == "product" and page.product_id:
            lines.append(
                f'The shopper is on the product page for "{page.product_name}" (product_id: {page.product_id}). '
                'When they say "this", "this one", "it", or "this item" without naming something else, they mean '
                "this product: use this product_id with your tools."
            )
        elif page and page.page == "products":
            lines.append(
                "The shopper is on the Products page"
                + (", which is currently showing your earlier search results." if page.showing_results else ", browsing the catalogue.")
            )
        elif page and page.page != "other":
            lines.append(f"The shopper is on the site's {page.page} page.")
        return "\n".join(lines)

    @agent.output_validator
    def grounded_reply(ctx: RunContext[ChatDeps], reply: AgentReply) -> AgentReply:
        found = {p.product_id for p in products_by_ids(reply.product_ids)}
        unknown = [i for i in reply.product_ids if i not in found]
        if unknown:
            raise ModelRetry(f"These product_ids do not exist: {unknown}. Only use product_ids returned by your tools.")
        problems = check_grounding(reply.message, ctx.messages)
        if problems:
            raise ModelRetry(" ".join(problems))
        return reply

    return agent


def to_message_history(history: list[HistoryMessage]) -> list[ModelMessage]:
    messages: list[ModelMessage] = []
    for item in history:
        if item.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=item.content)]))
        else:
            messages.append(ModelResponse(parts=[TextPart(content=item.content)]))
    return messages


async def respond(
    message: str,
    history: list[HistoryMessage],
    customer: CustomerProfile | None = None,
    page: PageContext | None = None,
) -> ChatResponse:
    """Run one chat turn and return the reply with its product cards."""
    run_id = uuid.uuid4().hex[:8]  # groups this turn's rows in output/audit_trail.json
    with capture_run_messages() as captured:
        try:
            result = await get_agent().run(
                message,
                deps=ChatDeps(customer=customer, page=page),
                message_history=to_message_history(history),
                usage_limits=UsageLimits(request_limit=MAX_MODEL_REQUESTS),
                model_settings={"timeout": REQUEST_TIMEOUT_SECONDS},
            )
        except AssistantUnavailable:
            raise  # the loop never started, so there is nothing to audit
        except ModelHTTPError as error:
            # The provider's content filter blocked the message: answer with a polite redirect, not an error.
            if error.status_code == 400 and "content management policy" in str(error.body).lower():
                record_audit(captured[len(history):], run_id, "content_filter", customer, "blocked by the provider's content filter")
                return ChatResponse(message=FILTERED_REPLY, products=[])
            record_audit(captured[len(history):], run_id, "error", customer, f"model call failed: HTTP {error.status_code}")
            raise
        except UnexpectedModelBehavior:
            # The model kept quoting numbers the database did not return; never show those to the shopper.
            record_audit(captured[len(history):], run_id, "grounding_failed", customer, "reply kept failing the price and stock check")
            return ChatResponse(message=UNVERIFIED_REPLY, products=[])
        except Exception as error:
            record_audit(captured[len(history):], run_id, "error", customer, f"{type(error).__name__}")
            raise
    record_audit(result.new_messages(), run_id, "stop", customer)
    reply = result.output
    cards = [ProductCard.from_product(p) for p in products_by_ids(reply.product_ids)[:MAX_PRODUCT_CARDS]]
    return ChatResponse(message=reply.message.strip(), products=cards, results=page_results(result.all_messages()))


def page_results(messages: list[ModelMessage]) -> SearchResults | None:
    """What the Products page should show, if the agent used show_on_page this turn (its last call counts)."""
    arguments = last_tool_arguments(messages, "show_on_page")
    if arguments is None:
        return None
    results, _, _ = build_page_results(**arguments)
    return results
