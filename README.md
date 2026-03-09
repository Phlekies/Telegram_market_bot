# Financial Assistant Bot for Telegram

Personal financial assistant on Telegram designed to monitor your favorite assets, answer quick market queries, and notify you only when something relevant happens.

Instead of manually checking charts, news, and finance apps all day, this bot acts as a proactive market watcher that works in the background and delivers the important information directly to your pocket.

---

## Overview

This project aims to build a **personal, automated, and proactive financial assistant** that lives inside Telegram.

The core idea is simple:

- ask for a price instantly,
- save your favorite assets,
- monitor them automatically,
- receive alerts when meaningful moves happen,
- and eventually get contextual news when volatility spikes.

It is not meant to be a trading bot or a portfolio execution platform.  
It is a **market monitoring and notification assistant** focused on saving time and reducing noise.

---

## Main Goals

The bot is designed around five main product goals:

1. **Fast market queries**
2. **Personalized asset memory**
3. **Volatility alerts**
4. **Daily market summaries**
5. **Contextual news in the future**

Together, these features turn the bot from a simple price checker into a real financial assistant.

---

## Core Features

### 1. Quick Queries — “The Oracle”

The most basic and immediate feature.

Instead of opening multiple apps or websites, the user can directly ask the bot for the price of an asset.

#### Example use cases

- “What is Bitcoin trading at?”
- “Tell me the current price of Apple”
- “Show me Ethereum price”

#### Expected behavior

The bot replies in seconds with a clean and direct response containing the current market price.

This makes Telegram a fast entry point to financial information.

---

### 2. Personalized Memory — “Your Asset Vault”

A generic bot can answer questions about any asset, but this project aims to make the bot **personal**.

Users can define and maintain their own watchlist.

#### Example use cases

- “Add Tesla to my watchlist”
- “Add BTC and ETH”
- “Remove Apple”
- “Show me my watchlist”

#### Expected behavior

The bot stores the selected assets and allows the user to retrieve them later with a single command or message.

This turns the system into a customized assistant rather than a public query tool.

---

### 3. Volatility Alerts — “The Watchdog”

This is the most important feature in the project.

The user defines rules, and the bot monitors the market in the background.

#### Example use cases

- “Alert me if any asset in my watchlist moves more than 5% in 24 hours”
- “Notify me if Bitcoin drops more than 3% today”
- “Warn me if Tesla jumps more than 4% intraday”

#### Expected behavior

The bot checks the configured assets periodically and sends a Telegram alert whenever a threshold is triggered.

Example alert:

> ⚠️ ALERT: Ethereum has dropped 6.2% in the last hour.

The main value here is that the user no longer needs to constantly monitor charts manually.

---

### 4. Morning Summary — “Your Financial Briefing”

The assistant should also help the user start the day with a quick market overview.

#### Example use cases

- daily briefing at a chosen time,
- market open status,
- watchlist performance snapshot,
- relevant trend summary.

#### Expected behavior

At a scheduled hour, the bot sends a structured message with:

- a quick market snapshot,
- the current status of the user’s watchlist,
- and notable changes or movements.

This is intended to reduce information overload and create a clean daily routine.

---

### 5. Future Evolution — “Contextual Analyst”

The long-term vision is not only to detect movement, but also to explain it.

When a relevant alert is triggered, the bot may search for the latest related financial headlines and attach them to the notification.

#### Example use cases

- price spike followed by related headlines,
- sudden drop with attached context,
- recent news linked to a company or crypto asset.

#### Expected behavior

The bot enriches alerts with a few relevant headlines so the user immediately understands possible reasons behind the move.

Example:

> ⚠️ ALERT: Tesla is down 5.8% today.  
> Related headlines:
> - [headline 1]
> - [headline 2]
> - [headline 3]

This is a future phase and not required for the first MVP.

---

## Why This Project?

Most users today interact with financial information in a reactive way:

- opening exchange apps,
- checking prices manually,
- switching between broker, charts, and news,
- and repeating the process many times a day.

This project changes that model.

The assistant is designed to be **proactive**:

- it watches the market for you,
- remembers what you care about,
- stays silent when nothing important happens,
- and speaks only when it matters.

In short:

**you stop chasing information, and information comes to you.**

---

## Product Philosophy

This project is built around a few simple principles:

### 1. Relevance over noise
The bot should not spam the user.  
Its value depends on notifying only when an event is meaningful.

### 2. Speed and clarity
Responses should be short, clean, and useful.

### 3. Personalization
The assistant should adapt to the user’s chosen assets and preferences.

### 4. Proactivity
The system should work in the background and reduce the need for manual monitoring.

### 5. Extensibility
The architecture should allow future growth, such as better summaries, richer alerts, and news context.

---

## Typical User Flow

A simple usage flow looks like this:

1. User opens the Telegram bot
2. User adds assets to a personal watchlist
3. User configures one or more alert rules
4. Bot monitors the selected assets automatically
5. Bot sends alerts only when relevant thresholds are crossed
6. User optionally requests current prices or portfolio snapshots at any time
7. Bot can also send daily summaries on schedule

This creates a continuous cycle of value with very little friction.

---

## Intended Use Cases

This project can be useful for:

- students interested in markets,
- retail investors,
- crypto users,
- people who want passive monitoring instead of active chart watching,
- users who want a lightweight financial assistant without opening multiple apps,
- and developers building finance-oriented automation tools.

It is especially useful for people who:

- follow a limited set of assets,
- care about large moves,
- and want concise updates rather than full dashboards.

---

## MVP Scope

The first useful version of the project should focus on the core value loop.

### MVP features

- query current asset price,
- add/remove assets from a personal watchlist,
- display watchlist,
- define simple percentage-based alerts,
- receive Telegram notifications when those alerts trigger.

This is enough to deliver real value.

---

## Future Roadmap

Possible future improvements include:

- multiple alert horizons: 1h / 24h / 7d,
- richer Telegram UI,
- better asset symbol resolution,
- daily and weekly summaries,
- alert deduplication and cooldown logic,
- linked financial headlines,
- short contextual summaries,
- sentiment or event classification,
- support for more asset classes.

---

## What This Project Is Not

To keep the project focused, it is important to clarify what it is **not**.

This is not:

- a high-frequency trading system,
- a broker,
- a portfolio execution tool,
- a financial advisor,
- or a guarantee of investment performance.

It is a **market monitoring assistant**.

---

## High-Level Conceptual Architecture

At a conceptual level, the project is divided into the following blocks:

- **Telegram interface**  
  Receives user commands and sends responses.

- **Intent handling layer**  
  Interprets what the user wants to do.

- **Market data layer**  
  Retrieves prices and variations.

- **User memory layer**  
  Stores watchlists, alerts, and preferences.

- **Alert engine**  
  Monitors rules and detects threshold events.

- **Scheduler / automation layer**  
  Runs periodic checks and summary jobs.

- **Context/news layer**  
  Optional future extension to enrich alerts.

---

## Example Commands / Interactions

Examples of the intended interaction style:

- `/price BTC`
- `/price AAPL`
- `/add TSLA`
- `/add ETH`
- `/remove BTC`
- `/watchlist`
- `/alert 5%`
- `/summary`
- “What is Bitcoin trading at?”
- “Add Ethereum to my watchlist”
- “Alert me if Tesla drops more than 4%”

The final command system may evolve, but the experience should remain simple and conversational.

---

## Main Value Proposition

The project can be summarized in one sentence:

> A personal financial watchdog on Telegram that monitors your assets, detects relevant moves, and delivers concise market information exactly when you need it.

---

## Status

This repository currently represents the **product idea, conceptual design, and planned feature set** of the project.

Implementation details, architecture decisions, infrastructure, APIs, and deployment setup will be added progressively as the project evolves.

---

## License

This project is currently under development.  
A license will be added once the repository structure is finalized.