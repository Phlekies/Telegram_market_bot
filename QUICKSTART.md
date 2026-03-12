# Quickstart - Bot de mercado crypto en Telegram

## 1) Crea tu bot y consigue el token
1. Abre Telegram y busca `@BotFather`.
2. Ejecuta `/newbot`.
3. Sigue los pasos y copia el token.

## 2) Configura variables en local
1. Copia `.env.example` a `.env`.
2. En `.env`, define:

```env
BOT_TOKEN=tu_token_de_botfather
TELEGRAM_API_BASE=https://api.telegram.org
COINGECKO_TOP100_URL=https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false&price_change_percentage=24h,7d,30d
COINGECKO_GLOBAL_URL=https://api.coingecko.com/api/v3/global
FEAR_GREED_API_URL=https://api.alternative.me/fng/?limit=7&format=json
MARKET_CACHE_TTL_SECONDS=300
```

`.env` no se sube a GitHub porque esta ignorado en `.gitignore`.

## 3) Instala dependencias
```bash
pip install -r requirements.txt
```

## 4) Ejecuta el bot
```bash
py -3 .\main.py
```

## 5) Comandos
- `/market` o `/indices` -> dashboard visual de mercado
- `/top100` -> lista completa del top 100 por market cap
- `/top100 2` -> pagina 2 del top 100
- `/top20` -> vista rapida del top 20
- `/price eth` -> snapshot de una cripto del top 100
- `/eth` o `/ada` -> atajo directo por simbolo
- `eth`, `ada`, `sol` -> atajo escribiendo solo simbolo
- `precio eth` -> frase natural
