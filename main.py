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

MARKET_PRICE_URL = os.getenv("MARKET_PRICE_URL", "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")

TELEGRAM_API = f"{TELEGRAM_API_BASE}/bot{TELEGRAM_TOKEN}"


def get_btc_price() -> float:
    response = requests.get(MARKET_PRICE_URL, timeout=10)
    response.raise_for_status()
    data = response.json()
    return float(data["price"])


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


def handle_message(message: dict) -> None:
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip().lower()

    if text in ("/start", "/help"):
        send_message(
            chat_id,
            "Comandos disponibles:\n"
            "- /btc\n"
            "- /price btc\n\n"
            "Tambien puedes escribir 'btc' o 'precio btc'.",
        )
        return

    if text in ("btc", "/btc", "/price", "/price btc", "precio btc", "bitcoin"):
        try:
            price = get_btc_price()
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            send_message(chat_id, f"BTC/USDT: {price:,.2f}\nActualizado: {timestamp}")
        except Exception as exc:
            send_message(chat_id, f"Error obteniendo el precio de BTC: {exc}")
        return

    send_message(
        chat_id,
        "No reconozco ese comando.\n"
        "Escribe /btc o /price btc para consultar el precio de Bitcoin.",
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


