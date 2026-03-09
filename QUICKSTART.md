# Quickstart - Bot de precio BTC en Telegram

## 1) Crea tu bot y consigue el token
1. Abre Telegram y busca `@BotFather`.
2. Ejecuta `/newbot`.
3. Sigue los pasos y copia el token.

## 2) Configura el token y APIs (solo en local)
1. Copia `.env.example` a `.env`.
2. En `.env`, define:

```env
BOT_TOKEN=tu_token_de_botfather
TELEGRAM_API_BASE=https://api.telegram.org
MARKET_PRICE_URL=https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT
```

`.env` no se sube a GitHub porque esta ignorado en `.gitignore`.

## 3) Instala dependencias
```bash
pip install -r requirements.txt
```

## 4) Ejecuta el bot
```bash
python main.py
```

## 5) Prueba comandos en Telegram
- `/start`
- `/btc`
- `/price btc`
- `btc`
- `precio btc`

El bot respondera con el precio actual de `BTC/USDT`.
