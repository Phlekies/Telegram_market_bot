import html
import math
import os
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("Falta BOT_TOKEN (o TELEGRAM_TOKEN) en el entorno (.env).")

TELEGRAM_API_BASE = os.getenv("TELEGRAM_API_BASE", "https://api.telegram.org")
TOP100_API_URL = os.getenv("COINGECKO_TOP100_URL") or os.getenv(
    "COINGECKO_TOP_URL",
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    "&sparkline=false&price_change_percentage=24h,7d,30d",
)
GLOBAL_API_URL = os.getenv(
    "COINGECKO_GLOBAL_URL",
    "https://api.coingecko.com/api/v3/global",
)
FEAR_GREED_API_URL = os.getenv(
    "FEAR_GREED_API_URL",
    "https://api.alternative.me/fng/?limit=7&format=json",
)
MARKET_CACHE_TTL_SECONDS = int(os.getenv("MARKET_CACHE_TTL_SECONDS", "300"))

TELEGRAM_API = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_TOKEN}"

MARKET_CACHE: dict = {
    "fetched_at": 0.0,
    "snapshot": None,
}


def send_message(chat_id: int, text: str, parse_mode: str = "HTML") -> None:
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()


def send_messages(chat_id: int, messages: list[str], parse_mode: str = "HTML") -> None:
    for message in messages:
        send_message(chat_id, message, parse_mode=parse_mode)


def get_updates(offset: int | None = None) -> dict:
    url = f"{TELEGRAM_API}/getUpdates"
    params = {"timeout": 30}
    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=35)
    response.raise_for_status()
    return response.json()


def fetch_json(url: str, timeout: int = 15) -> dict | list:
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def get_float(value: object, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_coin(raw_coin: dict) -> dict:
    return {
        "name": str(raw_coin.get("name", "Unknown")),
        "symbol": str(raw_coin.get("symbol", "")).upper(),
        "price": get_float(raw_coin.get("current_price")),
        "rank": int(raw_coin.get("market_cap_rank") or 0),
        "market_cap": get_float(raw_coin.get("market_cap")),
        "volume_24h": get_float(raw_coin.get("total_volume")),
        "change_24h": get_float(
            raw_coin.get("price_change_percentage_24h_in_currency"),
            get_float(raw_coin.get("price_change_percentage_24h")),
        ),
        "change_7d": get_float(raw_coin.get("price_change_percentage_7d_in_currency")),
        "change_30d": get_float(raw_coin.get("price_change_percentage_30d_in_currency")),
        "market_cap_change_24h": get_float(raw_coin.get("market_cap_change_24h")),
    }


def normalize_global(raw_global: dict) -> dict:
    return {
        "total_market_cap_usd": get_float(raw_global.get("total_market_cap", {}).get("usd")),
        "total_volume_usd": get_float(raw_global.get("total_volume", {}).get("usd")),
        "btc_dominance": get_float(raw_global.get("market_cap_percentage", {}).get("btc")),
        "eth_dominance": get_float(raw_global.get("market_cap_percentage", {}).get("eth")),
        "market_cap_change_24h_usd": get_float(raw_global.get("market_cap_change_percentage_24h_usd")),
        "active_cryptocurrencies": int(raw_global.get("active_cryptocurrencies") or 0),
        "markets": int(raw_global.get("markets") or 0),
    }


def normalize_fear_greed(raw_values: list[dict]) -> list[dict]:
    normalized = []
    for item in raw_values:
        normalized.append(
            {
                "value": int(item.get("value") or 0),
                "classification": str(item.get("value_classification", "Unknown")),
                "timestamp": item.get("timestamp"),
            }
        )
    return normalized


def fetch_market_snapshot(force_refresh: bool = False) -> dict:
    now = time.time()
    cached_snapshot = MARKET_CACHE.get("snapshot")
    is_fresh = (now - float(MARKET_CACHE["fetched_at"])) < MARKET_CACHE_TTL_SECONDS

    if cached_snapshot and is_fresh and not force_refresh:
        return cached_snapshot

    top100_raw = fetch_json(TOP100_API_URL)
    global_raw = fetch_json(GLOBAL_API_URL)
    fear_greed_raw = fetch_json(FEAR_GREED_API_URL)

    snapshot = {
        "top100": [normalize_coin(coin) for coin in top100_raw[:100]],
        "global": normalize_global(global_raw.get("data", {})),
        "fear_greed": normalize_fear_greed(fear_greed_raw.get("data", [])),
    }

    MARKET_CACHE["fetched_at"] = now
    MARKET_CACHE["snapshot"] = snapshot
    return snapshot


def find_coin(query: str, coins: list[dict]) -> dict | None:
    normalized = query.strip().lower()
    for coin in coins:
        if coin["symbol"].lower() == normalized or coin["name"].lower() == normalized:
            return coin
    return None


def format_price(value: float) -> str:
    if value >= 1000:
        return f"${value:,.2f}"
    if value >= 1:
        return f"${value:,.4f}"
    if value >= 0.01:
        return f"${value:,.6f}"
    return f"${value:,.8f}"


def format_money_compact(value: float) -> str:
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"
    if abs_value >= 1_000:
        return f"${value / 1_000:.2f}K"
    return f"${value:,.2f}"


def format_signed_money_compact(value: float) -> str:
    sign = "+" if value > 0 else "-" if value < 0 else ""
    return f"{sign}{format_money_compact(abs(value))}"


def format_signed_percent(value: float) -> str:
    return f"{value:+.2f}%"


def build_meter(ratio: float, width: int = 14, fill_char: str = "#") -> str:
    clamped_ratio = max(0.0, min(1.0, ratio))
    filled = int(round(clamped_ratio * width))
    return fill_char * filled + "." * (width - filled)


def build_signed_bar(value: float, max_ratio: float = 0.12, width: int = 12) -> str:
    ratio = min(abs(value) / max_ratio, 1.0)
    filled = int(round(ratio * width))
    char = "+" if value >= 0 else "-"
    return char * filled + "." * (width - filled)


def format_pre_block(text: str) -> str:
    return f"<pre>{html.escape(text)}</pre>"


def estimate_period_flow(coins: list[dict], period: str) -> float:
    total_flow = 0.0
    for coin in coins:
        market_cap = coin["market_cap"]
        if market_cap <= 0:
            continue

        if period == "24h":
            total_flow += coin["market_cap_change_24h"]
            continue

        pct_key = "change_7d" if period == "7d" else "change_30d"
        pct_change = coin[pct_key]
        denominator = 1 + (pct_change / 100)
        if denominator <= 0:
            continue

        previous_market_cap = market_cap / denominator
        total_flow += market_cap - previous_market_cap

    return total_flow


def classify_flow(flow_value: float, reference_market_cap: float) -> str:
    if reference_market_cap <= 0:
        return "flat"

    ratio = abs(flow_value) / reference_market_cap
    if ratio >= 0.08:
        return "muy fuerte"
    if ratio >= 0.04:
        return "fuerte"
    if ratio >= 0.015:
        return "moderada"
    return "suave"


def get_market_breadth(coins: list[dict]) -> tuple[int, int, int]:
    up = sum(1 for coin in coins if coin["change_24h"] > 0)
    down = sum(1 for coin in coins if coin["change_24h"] < 0)
    flat = len(coins) - up - down
    return up, down, flat


def get_top_movers(coins: list[dict], count: int = 3) -> tuple[list[dict], list[dict]]:
    sorted_coins = sorted(coins, key=lambda coin: coin["change_24h"], reverse=True)
    winners = sorted_coins[:count]
    losers = list(reversed(sorted_coins[-count:]))
    return winners, losers


def build_fear_greed_summary(values: list[dict]) -> tuple[str, float]:
    if not values:
        return "N/A", 0.0

    current = values[0]
    average = sum(item["value"] for item in values) / len(values)
    meter = build_meter(current["value"] / 100, width=12, fill_char="#")
    summary = f"{current['value']:>3}/100 {current['classification']:<15} [{meter}]"
    return summary, average


def build_flow_line(label: str, flow_value: float, reference_market_cap: float) -> str:
    direction = "IN " if flow_value > 0 else "OUT" if flow_value < 0 else "FLAT"
    intensity = classify_flow(flow_value, reference_market_cap)
    ratio = 0.0 if reference_market_cap <= 0 else flow_value / reference_market_cap
    bar = build_signed_bar(ratio)
    return f"{label:<4} {direction:<4} {format_signed_money_compact(flow_value):>11} {intensity:<10} [{bar}]"


def format_coin_message(coin: dict) -> str:
    trend_bar = build_signed_bar(coin["change_30d"] / 100, max_ratio=0.25, width=10)
    body = "\n".join(
        [
            f"Rank       #{coin['rank']}",
            f"Price      {format_price(coin['price'])}",
            f"24h        {format_signed_percent(coin['change_24h'])}",
            f"7d         {format_signed_percent(coin['change_7d'])}",
            f"30d        {format_signed_percent(coin['change_30d'])} [{trend_bar}]",
            f"Mkt Cap    {format_money_compact(coin['market_cap'])}",
            f"Vol 24h    {format_money_compact(coin['volume_24h'])}",
        ]
    )
    header = f"<b>{html.escape(coin['symbol'])} | {html.escape(coin['name'])}</b>"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    footer = f"<i>Snapshot: {html.escape(timestamp)}</i>"
    return "\n".join([header, format_pre_block(body), footer])


def format_market_dashboard(snapshot: dict) -> str:
    coins = snapshot["top100"]
    global_data = snapshot["global"]
    fear_greed = snapshot["fear_greed"]
    top100_market_cap = sum(coin["market_cap"] for coin in coins)
    flow_24h = estimate_period_flow(coins, "24h")
    flow_7d = estimate_period_flow(coins, "7d")
    flow_30d = estimate_period_flow(coins, "30d")
    up, down, flat = get_market_breadth(coins)
    winners, losers = get_top_movers(coins)
    fear_greed_line, fear_greed_avg = build_fear_greed_summary(fear_greed)

    lines = [
        "CRYPTO RADAR",
        "",
        f"Market Cap    {format_money_compact(global_data['total_market_cap_usd'])} ({format_signed_percent(global_data['market_cap_change_24h_usd'])})",
        f"Volume 24h    {format_money_compact(global_data['total_volume_usd'])}",
        f"Dominance     BTC {global_data['btc_dominance']:.2f}% | ETH {global_data['eth_dominance']:.2f}%",
        f"Breadth       {up} up | {down} down | {flat} flat",
        "",
        f"Fear & Greed  {fear_greed_line}",
        f"7d avg        {fear_greed_avg:.1f}/100",
        "",
        "Flow proxy (top 100 market cap)",
        build_flow_line("24h", flow_24h, top100_market_cap),
        build_flow_line("7d", flow_7d, top100_market_cap),
        build_flow_line("30d", flow_30d, top100_market_cap),
        "",
        "Top movers 24h",
        " | ".join(f"{coin['symbol']} {format_signed_percent(coin['change_24h'])}" for coin in winners),
        "Bottom 24h",
        " | ".join(f"{coin['symbol']} {format_signed_percent(coin['change_24h'])}" for coin in losers),
    ]

    header = "<b>Market Snapshot</b>"
    body = format_pre_block("\n".join(lines))
    footer = (
        "<i>Flow proxy = estimacion agregada del cambio de market cap del top 100. "
        "Es una aproximacion util, no un flujo neto oficial.</i>"
    )
    return "\n".join([header, body, footer])


def build_top_list_message(coins: list[dict], title: str, page: int, total_pages: int) -> str:
    lines = [f"{'RANK':>4} {'SYM':<6} {'PRICE':>13} {'24H':>8} {'MKT CAP':>10}"]
    for coin in coins:
        lines.append(
            f"{coin['rank']:>4} "
            f"{coin['symbol']:<6} "
            f"{format_price(coin['price']):>13} "
            f"{format_signed_percent(coin['change_24h']):>8} "
            f"{format_money_compact(coin['market_cap']):>10}"
        )

    header = f"<b>{html.escape(title)} | pagina {page}/{total_pages}</b>"
    return "\n".join([header, format_pre_block("\n".join(lines))])


def format_top_messages(coins: list[dict], chunk_size: int = 25, requested_page: int | None = None) -> list[str]:
    if requested_page is not None:
        total_pages = math.ceil(len(coins) / chunk_size)
        if requested_page < 1 or requested_page > total_pages:
            return [
                "<b>Pagina no valida</b>\n"
                + format_pre_block(f"Usa un numero entre 1 y {total_pages}. Ejemplo: /top100 2")
            ]
        start = (requested_page - 1) * chunk_size
        end = start + chunk_size
        return [
            build_top_list_message(
                coins[start:end],
                "Top 100 por market cap",
                requested_page,
                total_pages,
            )
        ]

    messages = []
    total_pages = math.ceil(len(coins) / chunk_size)
    for page in range(total_pages):
        start = page * chunk_size
        end = start + chunk_size
        messages.append(
            build_top_list_message(
                coins[start:end],
                "Top 100 por market cap",
                page + 1,
                total_pages,
            )
        )
    return messages


def extract_symbol_from_price_command(text: str) -> str | None:
    parts = text.split(maxsplit=1)
    if len(parts) < 2:
        return None
    return parts[1].strip()


def handle_message(message: dict) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    text_lower = text.lower()

    if text_lower in ("/start", "/help"):
        send_message(
            chat_id,
            "\n".join(
                [
                    "<b>Comandos disponibles</b>",
                    format_pre_block(
                        "\n".join(
                            [
                                "/market o /indices   -> dashboard de mercado",
                                "/top100 [pagina]     -> ranking completo",
                                "/top20               -> vista rapida del top 20",
                                "/price <symbol>      -> precio y datos de una moneda",
                                "/<symbol>            -> atajo directo, ej /eth",
                                "precio <symbol>      -> texto natural, ej precio ada",
                                "btc, eth, sol...     -> simbolo directo",
                            ]
                        )
                    ),
                ]
            ),
        )
        return

    try:
        snapshot = fetch_market_snapshot()
    except Exception as exc:
        send_message(chat_id, f"Error obteniendo datos de mercado: {html.escape(str(exc))}")
        return

    coins = snapshot["top100"]

    if text_lower in ("/market", "/indices", "/overview", "mercado", "indices"):
        send_message(chat_id, format_market_dashboard(snapshot))
        return

    if text_lower.startswith("/top100"):
        page = None
        parts = text.split(maxsplit=1)
        if len(parts) == 2 and parts[1].strip().isdigit():
            page = int(parts[1].strip())
        send_messages(chat_id, format_top_messages(coins, chunk_size=25, requested_page=page))
        return

    if text_lower == "/top20":
        send_message(chat_id, build_top_list_message(coins[:20], "Top 20 por market cap", 1, 1))
        return

    if text.startswith("/") and " " not in text and text_lower not in (
        "/start",
        "/help",
        "/market",
        "/indices",
        "/overview",
        "/top100",
        "/top20",
    ):
        query = text[1:].strip()
        coin = find_coin(query, coins)
        if coin:
            send_message(chat_id, format_coin_message(coin))
        else:
            send_message(chat_id, f"{html.escape(query.upper())} no esta en el top 100 actual. Usa /top100.")
        return

    if text_lower.startswith("/price"):
        query = extract_symbol_from_price_command(text)
        if not query:
            send_message(chat_id, "Uso: /price <symbol>. Ejemplo: /price btc")
            return

        coin = find_coin(query, coins)
        if coin:
            send_message(chat_id, format_coin_message(coin))
        else:
            send_message(chat_id, f"{html.escape(query.upper())} no esta en el top 100 actual. Usa /top100.")
        return

    if text_lower.startswith("precio "):
        query = extract_symbol_from_price_command(text)
        if not query:
            send_message(chat_id, "Uso: precio <symbol>. Ejemplo: precio eth")
            return

        coin = find_coin(query, coins)
        if coin:
            send_message(chat_id, format_coin_message(coin))
        else:
            send_message(chat_id, f"{html.escape(query.upper())} no esta en el top 100 actual. Usa /top100.")
        return

    coin = find_coin(text, coins)
    if coin:
        send_message(chat_id, format_coin_message(coin))
        return

    send_message(
        chat_id,
        "No reconozco ese comando.\n"
        + format_pre_block("Usa /market, /top100, /price <symbol> o escribe directamente un simbolo."),
    )


def main() -> None:
    print("Bot iniciado...")
    last_update_id = None

    while True:
        try:
            data = get_updates(offset=last_update_id)
            if not data.get("ok"):
                time.sleep(2)
                continue

            for update in data.get("result", []):
                last_update_id = update["update_id"] + 1

                message = update.get("message")
                if message and "text" in message:
                    handle_message(message)

        except requests.RequestException as exc:
            print(f"Error de red: {exc}")
            time.sleep(3)
        except Exception as exc:
            print(f"Error inesperado: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    main()
