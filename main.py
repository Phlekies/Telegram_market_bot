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
TOP20_API_URL = os.getenv(
    "COINGECKO_TOP_URL",
    "https://api.coingecko.com/api/v3/coins/markets"
    "?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false",
)
TOP_CACHE_TTL_SECONDS = int(os.getenv("TOP_CACHE_TTL_SECONDS", "300"))

TELEGRAM_API = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_TOKEN}"

TOP20_CACHE: dict = {
    "fetched_at": 0.0,
    "data": [],
}


def send_message(chat_id: int, text: str) -> None:
    url = f"{TELEGRAM_API}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
    }
    response = requests.post(url, json=payload, timeout=10)
    response.raise_for_status()


def get_updates(offset: int | None = None) -> dict:
    url = f"{TELEGRAM_API}/getUpdates"
    params = {
        "timeout": 30,
    }
    if offset is not None:
        params["offset"] = offset

    response = requests.get(url, params=params, timeout=35)
    response.raise_for_status()
    return response.json()


def fetch_top20_cryptos(force_refresh: bool = False) -> list[dict]:
    now = time.time()
    has_cache = bool(TOP20_CACHE["data"])
    cache_is_fresh = (now - float(TOP20_CACHE["fetched_at"])) < TOP_CACHE_TTL_SECONDS

    if has_cache and cache_is_fresh and not force_refresh:
        return TOP20_CACHE["data"]

    response = requests.get(TOP20_API_URL, timeout=15)
    response.raise_for_status()
    data = response.json()

    top20 = []
    for coin in data[:20]:
        top20.append(
            {
                "name": coin.get("name", "Unknown"),
                "symbol": str(coin.get("symbol", "")).upper(),
                "price": float(coin.get("current_price", 0.0)),
            }
        )

    TOP20_CACHE["fetched_at"] = now
    TOP20_CACHE["data"] = top20
    return top20


def find_coin(symbol: str, top20: list[dict]) -> dict | None:
    normalized = symbol.strip().upper()
    for coin in top20:
        if coin["symbol"] == normalized:
            return coin
    return None


def format_top20_message(top20: list[dict]) -> str:
    lines = ["Top 20 criptomonedas (market cap):"]
    for idx, coin in enumerate(top20, start=1):
        lines.append(f"{idx:02d}. {coin['symbol']} ({coin['name']}): ${coin['price']:,.4f}")

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines.append("")
    lines.append(f"Actualizado: {timestamp}")
    return "\n".join(lines)


def format_price_message(coin: dict) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    return f"{coin['symbol']} ({coin['name']}): ${coin['price']:,.4f}\nActualizado: {timestamp}"


def handle_message(message: dict) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()
    text_lower = text.lower()

    if text_lower in ("/start", "/help"):
        send_message(
            chat_id,
            "Comandos disponibles:\n"
            "- /top20 (lista top 20 criptomonedas)\n"
            "- /price <symbol> (ej: /price btc)\n"
            "- /<symbol> (ej: /eth, /ada)\n"
            "- precio <symbol> (ej: precio eth)\n"
            "- btc, eth, sol... (atajo para simbolos del top 20)",
        )
        return

    try:
        top20 = fetch_top20_cryptos()
    except Exception as exc:
        send_message(chat_id, f"Error obteniendo el top 20: {exc}")
        return

    if text_lower == "/top20":
        send_message(chat_id, format_top20_message(top20))
        return

    # Comando corto tipo /eth, /ada, /btc...
    if text.startswith("/") and " " not in text and text_lower not in ("/start", "/help", "/top20"):
        symbol = text[1:].strip().upper()
        coin = find_coin(symbol, top20)
        if coin:
            send_message(chat_id, format_price_message(coin))
        else:
            send_message(chat_id, f"{symbol} no esta en el top 20 actual. Usa /top20 para verlo.")
        return

    if text_lower.startswith("/price"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "Uso: /price <symbol>. Ejemplo: /price btc")
            return

        symbol = parts[1].strip().upper()
        coin = find_coin(symbol, top20)
        if not coin:
            send_message(chat_id, f"{symbol} no esta en el top 20 actual. Usa /top20 para verlo.")
            return

        send_message(chat_id, format_price_message(coin))
        return

    # Frase natural sencilla: "precio eth"
    if text_lower.startswith("precio "):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "Uso: precio <symbol>. Ejemplo: precio eth")
            return

        symbol = parts[1].strip().upper()
        coin = find_coin(symbol, top20)
        if coin:
            send_message(chat_id, format_price_message(coin))
        else:
            send_message(chat_id, f"{symbol} no esta en el top 20 actual. Usa /top20 para verlo.")
        return

    # Atajo: si escriben solo el simbolo (btc, eth, sol...), respondemos precio.
    coin = find_coin(text, top20)
    if coin:
        send_message(chat_id, format_price_message(coin))
        return

    send_message(
        chat_id,
        "No reconozco ese comando.\n"
        "Usa /top20, /price <symbol> o /<symbol>.",
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
