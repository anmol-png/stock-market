# Personal Daily Intelligence Agent — Build Plan

**Goal:** A fully-automated daily analyst with **two pillars** — a *decoded* **World** news feed
(everything you shouldn't miss, explained) and a **Markets** engine (US + India + crypto/commodities,
with in-house technical analysis and every metric explained). It emails a short digest and maintains
an intuitive dashboard with the full depth. Built **free / near-free**, with the AI brain running on
your **Claude Max subscription (not the paid API)**.

**Design principle:** the reader is new to markets and world affairs — so the product *decodes and
explains* rather than summarizing. No bare numbers, no raw headlines: what it is, why it matters,
what it sets in motion.

---

## 1. The core idea (why this is basically free)

Instead of paying per-token for an API, **Claude Code itself is the engine.** A scheduled cloud
agent (a "routine") wakes up every morning on your subscription and:

1. Runs small Python scripts that pull **free** world news + market data (US, India, crypto).
2. Reads it and **decodes/analyzes as itself** — no API tokens billed.
3. Uses built-in **web search/fetch** to confirm facts and grab the day's top global stories.
4. Writes two briefs (World + Markets) + refreshes the dashboard's per-stock analysis.
5. Sends a short email and publishes the full-depth dashboard.

Your subscription covers the intelligence, reasoning, and web access. Everything else below is on a
free tier.

```
  ┌───────────────────────────────────────────────────────────────┐
  │  SCHEDULED CLAUDE CODE ROUTINE  (runs ~7:00am on your Max sub)  │
  │                                                                 │
  │   fetch_world.py ─► broad global news (all categories)          │
  │   fetch.py       ─► free market data + news (US / India / crypto)│
  │   analyze_stock.py ─► technical verdict per stock                │
  │        │                                                        │
  │        ▼                                                        │
  │   Claude decodes + analyzes (as the model, no API cost)         │
  │   + WebSearch to confirm & fill gaps                            │
  │        │                                                        │
  │        ├──► world.json  (decoded "don't miss" global stories)   │
  │        ├──► brief.json  (what-to-watch, favorites, risks)       │
  │        ├──► send.py ─────► short EMAIL digest (Gmail SMTP)       │
  │        └──► git push ────► DASHBOARD (GitHub Pages, free)        │
  └───────────────────────────────────────────────────────────────┘
```

---

## 2. The stack — every layer, all free

| Layer | Choice (free) | Notes |
|---|---|---|
| **Brain + orchestration** | Scheduled **Claude Code routine** (`/schedule`) | Runs on your Max sub. Fallback: local `cron` + `claude -p` headless, or GitHub Actions to trigger. |
| **US data** | `yfinance` (free) + **Finnhub free** (60 calls/min) | yfinance = quotes/history; Finnhub = company news, earnings + economic calendar, filings. |
| **India data** | `yfinance` with `.NS` / `.BO` suffixes (free, no account) | e.g. `RELIANCE.NS`, `TCS.NS`. For true real-time later: **Angel One SmartAPI** or **Fyers** (free with a demat account). |
| **Crypto / commodities** | **CoinGecko** free API + `yfinance` (`GC=F` gold, `^NSEI` Nifty, `^GSPC` S&P) | Abundant free 24/7 data. |
| **News + headlines** | **Finnhub news** + **GDELT** (free global tone) + **RSS** feeds + Claude **WebSearch** | WebSearch (free on your sub) is the secret weapon for "around the world" coverage. |
| **Calendars** | Finnhub earnings + economic calendar (free) | Drives the "don't miss" catalysts module. |
| **Email delivery** | **Gmail SMTP** (app password, free) *or* **Resend** free tier (3,000/mo) | Headless-safe. Gmail MCP may not exist in a cloud routine — use SMTP/Resend. |
| **Dashboard** | Static site on **GitHub Pages** (free) + free **TradingView widgets** | Best "real app" feel with near-zero code. Live charts/heatmaps/watchlists from TradingView; AI brief regenerated daily. |
| **Storage/state** | Flat files in the git repo (`output/*.json`) | No database needed for one user. |
| **Intraday alerts (Phase 2, optional)** | GitHub Actions cron every 30 min in market hours → Telegram/email on big moves | Keep out of v1; add once the daily flow is solid. |

**Total monthly cost: ~$0** (subscription already paid). The only "cost" is a demat account *if* you
later want real-time India data — and that's free to open (you pay brokerage only when you trade).

---

## 3. The dashboard — two decoded pillars, for free

A static HTML site on **GitHub Pages** with a tab switch between two pillars. We deliberately **do not**
use a wall of third-party widgets — the earlier TradingView-widget version felt cluttered and generic.
Instead we compute and *explain* everything ourselves.

**🌍 World** — a decoded news feed. Each story: what happened → why it matters → (expand) ripple
effects → why you're seeing it now → what to watch → market link. Plus a "big picture" throughline and
category filters. Raw headlines come from `fetch_world.py`; Claude decodes the important ones.

**📈 Markets** — knowledge-driven, not search-first. A "don't miss" hero, a market at-a-glance, and a
processed **verdict per stock** (Strong Buy … Strong Sell) from our own indicator engine
(`analyze_stock.py`). Click any stock → a deep panel with a plain-English read, MA/oscillator ratings,
key levels, 52-week position, volatility, an own-drawn price chart, and every indicator as a signal.

**The education layer (`glossary.js`)** — the fix for "I don't know what I'm looking at." Every metric
(RSI, MACD, ADX, P/E, beta, 52-week range…) has a tap-to-open **ⓘ** explaining, in beginner terms, what
it is, how to read the value you're seeing, and why it matters. Nothing is a bare number.

Layout sketch:

```
┌──────────────────────────────────────────────────────────┐
│  🧭 Daily Intelligence        [ 🌍 World ] [ 📈 Markets ] │  ← tab switch
├──────────────────────────────────────────────────────────┤
│  WORLD: the big picture (throughline)                     │
│  #1 story  what happened · why it matters · ▾ ripple/why  │  ← decoded, ranked
│  #2 story ...                    [filter: geo/econ/tech…] │
│  ─────────────────────────────────────────────────────── │
│  MARKETS: ▲ Don't Miss · at-a-glance · verdict per stock  │
│  click a stock → deep panel, every metric has an ⓘ        │
└──────────────────────────────────────────────────────────┘
```

---

## 4. The "expert analyst" persona

A `CLAUDE.md` in the repo defines how the agent thinks, so every run is consistent and disciplined:

- **Role:** a seasoned global macro + equities analyst. Calm, concise, ranks by materiality.
- **Method:** overnight moves → today's catalysts → what changed for favorites → risks → "what to
  watch." Always distinguishes signal from noise.
- **Guardrails:** cite sources; label as **not financial advice**; never invent numbers — if data is
  missing, say so; no trade-execution authority.
- **Output contract:** writes a strict `brief.json` (so the email + dashboard render deterministically).

---

## 5. Daily flow (what happens at 7:00am)

1. **Fetch** — `fetch.py` pulls overnight OHLC + fundamentals for your watchlist/favorites (US via
   yfinance/Finnhub; India via `.NS`/`.BO`; crypto via CoinGecko), plus Finnhub news + calendars and
   a few RSS feeds → writes `output/raw-YYYY-MM-DD.json`.
2. **Analyze** — the routine reads the raw data, adds **WebSearch** for top global headlines, and
   produces the expert brief → `output/brief-YYYY-MM-DD.json` (ranked "what to watch", global summary,
   per-favorite deep cards, risks, catalysts).
3. **Render + send** — `send.py` turns the brief into a clean, single-column, mobile-friendly HTML
   email (charts as static images or TradingView links) and sends it.
4. **Publish** — `build.py` injects the brief into `dashboard/index.html`; the routine commits and
   pushes → GitHub Pages updates automatically.

Everything is idempotent and re-runnable, and every brief is archived in the repo for history.

---

## 6. Phased rollout

**Weekend 1 — the email works.**
Free accounts (Finnhub key, Gmail app password or Resend, GitHub). Write `config/watchlist.yml` +
`favorites.yml`, `fetch.py`, `CLAUDE.md`, and a simple `send.py`. Run it manually until the digest
looks great in your inbox.

**Weekend 2 — automate it.**
Set up the scheduled routine with `/schedule` so it runs every morning on your subscription. Tune the
prompt until the "what to watch" section is genuinely sharp and scannable.

**Weekend 3 — the dashboard.**
Build the static GitHub Pages site with TradingView widgets + the AI-brief panel; have the routine
publish it daily. Add favorite-stock detail cards.

**Later (optional) — intraday + India real-time.**
Add a GitHub Actions "big-move watcher" (every 30 min in market hours) that pings you on Telegram, and
wire Angel One/Fyers for real-time NSE/BSE if you want tick-level India data.

---

## 7. What to set up first (all free, ~15 min)

1. **Finnhub** account → free API key (news + calendars).
2. **Gmail app password** (needs 2FA on) *or* a **Resend** account → API key.
3. A **GitHub** repo (for the dashboard on GitHub Pages).
4. *(optional, for real-time India later)* an **Angel One** or **Fyers** demat account → free API key.

---

## 8. Honest limitations

- **Free data is delayed** (~15 min) or EOD for US, and `yfinance` is an unofficial feed that can
  occasionally break. Fine for a daily brief and big-move alerts; not for day-trading.
- **India is the hardest free path** — no cheap official real-time NSE/BSE announcements API. `.NS`
  quotes + WebSearch + Screener.in/Trendlyne (web) cover most needs; a free broker API removes the
  gap if you open an account.
- **Cloud routines run headless** — use SMTP/Resend for email (not the interactive Gmail integration),
  and store secrets (Finnhub key, email password, git token) as routine/repo secrets, never in code.
- **This is decision-support, not advice.** Sentiment scores and AI summaries can miss nuance; the
  agent is tuned to flag, rank, and explain — you decide.
```
