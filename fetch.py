#!/usr/bin/env python3
"""Pull free market data + news for the daily brief.

Sources (all free): yfinance (prices/history/fundamentals for US + India + crypto + commodities),
Finnhub free tier (company news, general news, earnings/economic calendars — optional), CoinGecko
(crypto prices), and RSS feeds (headlines). Writes:

    output/raw-<YYYY-MM-DD>.json   (dated archive)
    output/raw-latest.json         (what the analyst reads)

Nothing here is a paid API. Finnhub is optional; without a key it is skipped.
Run:  python fetch.py
"""
from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import sys

import requests
import yaml

try:
    import yfinance as yf
except ImportError:
    print("Missing dependency 'yfinance'. Run: pip install -r requirements.txt", file=sys.stderr)
    raise

try:
    import feedparser
except ImportError:
    feedparser = None

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

FINNHUB_KEY = os.getenv("FINNHUB_API_KEY", "").strip()
TODAY = dt.date.today()
NOW_ISO = dt.datetime.now().astimezone().isoformat(timespec="seconds")

# A few free finance RSS feeds (US + India). Edit freely.
RSS_FEEDS = [
    ("CNBC Markets", "https://www.cnbc.com/id/20910258/device/rss/rss.html"),
    ("Reuters Business", "https://feeds.reuters.com/reuters/businessNews"),
    ("Economic Times Markets", "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms"),
    ("Moneycontrol Business", "https://www.moneycontrol.com/rss/business.xml"),
]

HTTP_TIMEOUT = 20


def load_yaml(rel_path: str) -> dict:
    with open(ROOT / rel_path) as f:
        return yaml.safe_load(f) or {}


# ----------------------------- price / indicator helpers -----------------------------

def _pct(last: float, prev: float) -> float:
    return round((last / prev - 1.0) * 100.0, 2) if prev else 0.0


def snapshot(ticker: str) -> dict | None:
    """Light snapshot: last close, prev close, % change. Used for the broad watchlist."""
    try:
        hist = yf.Ticker(ticker).history(period="5d", auto_adjust=False)
        if hist.empty:
            return None
        close = hist["Close"].dropna()
        last = float(close.iloc[-1])
        prev = float(close.iloc[-2]) if len(close) > 1 else last
        return {"ticker": ticker, "price": round(last, 4), "change_pct": _pct(last, prev)}
    except Exception as e:  # noqa: BLE001 - never let one ticker break the run
        print(f"  ! snapshot failed for {ticker}: {e}", file=sys.stderr)
        return None


def _rsi(close, period: int = 14) -> float | None:
    try:
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(period).mean()
        loss = (-delta.clip(upper=0)).rolling(period).mean()
        rs = gain / loss
        rsi = 100 - 100 / (1 + rs)
        val = rsi.iloc[-1]
        return round(float(val), 1) if val == val else None  # NaN check
    except Exception:  # noqa: BLE001
        return None


def deep_snapshot(fav: dict) -> dict:
    """Rich snapshot for a favorite: price, indicators, fundamentals."""
    ticker = fav["ticker"]
    out = {"ticker": ticker, "name": fav.get("name", ticker), "note": fav.get("note", "")}
    try:
        tkr = yf.Ticker(ticker)
        hist = tkr.history(period="1y", auto_adjust=False)
        if not hist.empty:
            close = hist["Close"].dropna()
            last = float(close.iloc[-1])
            prev = float(close.iloc[-2]) if len(close) > 1 else last
            window = close.tail(252)
            out.update(
                price=round(last, 4),
                change_pct=_pct(last, prev),
                dma50=round(float(close.rolling(50).mean().iloc[-1]), 2) if len(close) >= 50 else None,
                dma200=round(float(close.rolling(200).mean().iloc[-1]), 2) if len(close) >= 200 else None,
                high_52w=round(float(window.max()), 2),
                low_52w=round(float(window.min()), 2),
                rsi14=_rsi(close),
            )
        # Fundamentals via .info can be slow/flaky — best effort only.
        try:
            info = tkr.info or {}
            out["fundamentals"] = {
                k: info.get(k)
                for k in (
                    "sector", "industry", "marketCap", "trailingPE", "forwardPE",
                    "profitMargins", "revenueGrowth", "dividendYield", "beta",
                    "fiftyTwoWeekHigh", "fiftyTwoWeekLow",
                )
                if info.get(k) is not None
            }
        except Exception:  # noqa: BLE001
            out["fundamentals"] = {}
    except Exception as e:  # noqa: BLE001
        print(f"  ! deep_snapshot failed for {ticker}: {e}", file=sys.stderr)

    # Company news from Finnhub (US symbols only).
    if FINNHUB_KEY and fav.get("finnhub"):
        out["news"] = finnhub_company_news(fav["finnhub"])
    # Crypto spot from CoinGecko (nice-to-have; yfinance already gave price).
    if fav.get("coingecko"):
        cg = coingecko_price([fav["coingecko"]])
        if fav["coingecko"] in cg:
            out["coingecko"] = cg[fav["coingecko"]]
    return out


# ----------------------------- Finnhub (optional, free) -----------------------------

def _finnhub_get(path: str, params: dict) -> object:
    params = {**params, "token": FINNHUB_KEY}
    try:
        r = requests.get(f"https://finnhub.io/api/v1{path}", params=params, timeout=HTTP_TIMEOUT)
        if r.status_code == 200:
            return r.json()
        print(f"  ! finnhub {path} -> HTTP {r.status_code}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"  ! finnhub {path} failed: {e}", file=sys.stderr)
    return None


def finnhub_general_news(limit: int = 20) -> list:
    data = _finnhub_get("/news", {"category": "general"})
    if not isinstance(data, list):
        return []
    return [
        {"source": n.get("source"), "headline": n.get("headline"), "url": n.get("url"),
         "datetime": n.get("datetime"), "summary": (n.get("summary") or "")[:400]}
        for n in data[:limit]
    ]


def finnhub_company_news(symbol: str, days_back: int = 3, limit: int = 6) -> list:
    frm = (TODAY - dt.timedelta(days=days_back)).isoformat()
    data = _finnhub_get("/company-news", {"symbol": symbol, "from": frm, "to": TODAY.isoformat()})
    if not isinstance(data, list):
        return []
    return [
        {"headline": n.get("headline"), "url": n.get("url"), "source": n.get("source"),
         "summary": (n.get("summary") or "")[:300]}
        for n in data[:limit]
    ]


def finnhub_calendars() -> dict:
    out = {"earnings": [], "economic": []}
    frm = TODAY.isoformat()
    to = (TODAY + dt.timedelta(days=2)).isoformat()
    earn = _finnhub_get("/calendar/earnings", {"from": frm, "to": to})
    if isinstance(earn, dict):
        out["earnings"] = earn.get("earningsCalendar", [])[:30]
    econ = _finnhub_get("/calendar/economic", {})
    if isinstance(econ, dict):
        rows = econ.get("economicCalendar", []) or []
        out["economic"] = [r for r in rows if r.get("time", "").startswith(frm)][:30]
    return out


# ----------------------------- CoinGecko (free) -----------------------------

def coingecko_price(ids: list[str]) -> dict:
    if not ids:
        return {}
    try:
        r = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": ",".join(ids), "vs_currencies": "usd",
                    "include_24hr_change": "true", "include_market_cap": "true"},
            timeout=HTTP_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json()
        print(f"  ! coingecko -> HTTP {r.status_code}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"  ! coingecko failed: {e}", file=sys.stderr)
    return {}


# ----------------------------- RSS (free) -----------------------------

def rss_headlines(per_feed: int = 6) -> list:
    if feedparser is None:
        return []
    items = []
    for name, url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:per_feed]:
                items.append({
                    "source": name,
                    "headline": entry.get("title"),
                    "url": entry.get("link"),
                    "published": entry.get("published", ""),
                })
        except Exception as e:  # noqa: BLE001
            print(f"  ! rss {name} failed: {e}", file=sys.stderr)
    return items


# ----------------------------- main -----------------------------

def collect_group(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows or []:
        snap = snapshot(row["ticker"])
        if snap:
            snap["name"] = row.get("name", row["ticker"])
            out.append(snap)
    return out


def main() -> None:
    watch = load_yaml("config/watchlist.yml")
    favs = load_yaml("config/favorites.yml").get("favorites", [])

    print("Fetching market data (free sources)...")
    markets = {
        "us_indices": collect_group(watch.get("us_indices")),
        "us_stocks": collect_group(watch.get("us_stocks")),
        "india_indices": collect_group(watch.get("india_indices")),
        "india_stocks": collect_group(watch.get("india_stocks")),
        "crypto": collect_group(watch.get("crypto")),
        "commodities": collect_group(watch.get("commodities")),
    }

    # Enrich crypto with CoinGecko 24h change where available.
    cg_ids = [c["coingecko"] for c in watch.get("crypto", []) if c.get("coingecko")]
    cg = coingecko_price(cg_ids)
    for c in watch.get("crypto", []):
        cid = c.get("coingecko")
        if cid and cid in cg:
            for m in markets["crypto"]:
                if m["ticker"] == c["ticker"]:
                    m["coingecko"] = cg[cid]

    print("Fetching favorites (deep)...")
    favorites = [deep_snapshot(f) for f in favs]

    print("Fetching news + calendars...")
    news = rss_headlines()
    if FINNHUB_KEY:
        news = finnhub_general_news() + news
    calendar = finnhub_calendars() if FINNHUB_KEY else {"earnings": [], "economic": []}

    raw = {
        "date": TODAY.isoformat(),
        "as_of": NOW_ISO,
        "markets": markets,
        "favorites": favorites,
        "news": news,
        "calendar": calendar,
        "sources": {
            "prices": "yfinance",
            "news": ["finnhub" if FINNHUB_KEY else None, "rss"],
            "crypto": "coingecko",
            "finnhub_enabled": bool(FINNHUB_KEY),
        },
    }

    dated = OUT / f"raw-{TODAY.isoformat()}.json"
    latest = OUT / "raw-latest.json"
    for path in (dated, latest):
        with open(path, "w") as f:
            json.dump(raw, f, indent=2, default=str)

    n_prices = sum(len(v) for v in markets.values())
    print(f"Done. {n_prices} instruments, {len(favorites)} favorites, {len(news)} headlines.")
    print(f"Wrote {latest.relative_to(ROOT)} (and dated copy).")


if __name__ == "__main__":
    main()
