#!/usr/bin/env python3
"""Industry-standard technical analysis for any ticker — processed into a clear verdict.

Computes the standard indicator suite (moving averages, RSI, MACD, Stochastic, CCI, Williams %R,
ADX, ATR, Bollinger, OBV, momentum), turns each into a Buy/Sell/Neutral signal, aggregates them
into a TradingView-style rating (Strong Buy … Strong Sell), derives trend, support/resistance,
volatility, and a plain-English summary. Writes a clean per-stock JSON the dashboard reads.

Usage:
    python analyze_stock.py AAPL
    python analyze_stock.py RELIANCE.NS TCS.NS
    python analyze_stock.py --all      # every ticker in config/watchlist.yml + favorites.yml
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import pathlib
import sys

import numpy as np
import pandas as pd

try:
    import yfinance as yf
except ImportError:
    print("Missing 'yfinance'. Run: pip install -r requirements.txt", file=sys.stderr)
    raise

try:
    import yaml
except ImportError:
    yaml = None

ROOT = pathlib.Path(__file__).resolve().parent
STOCKS = ROOT / "dashboard" / "stocks"
STOCKS.mkdir(parents=True, exist_ok=True)


# --------------------------- indicator math (industry standard) ---------------------------

def _sma(s, n):
    return s.rolling(n).mean()


def _ema(s, n):
    return s.ewm(span=n, adjust=False).mean()


def _rsi(close, n=14):
    d = close.diff()
    gain = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def _macd(close, fast=12, slow=26, sig=9):
    line = _ema(close, fast) - _ema(close, slow)
    signal = _ema(line, sig)
    return line, signal, line - signal


def _stoch(high, low, close, n=14, d=3):
    ll = low.rolling(n).min()
    hh = high.rolling(n).max()
    k = 100 * (close - ll) / (hh - ll).replace(0, np.nan)
    return k, k.rolling(d).mean()


def _cci(high, low, close, n=20):
    tp = (high + low + close) / 3
    ma = tp.rolling(n).mean()
    md = (tp - ma).abs().rolling(n).mean()
    return (tp - ma) / (0.015 * md.replace(0, np.nan))


def _williams_r(high, low, close, n=14):
    hh = high.rolling(n).max()
    ll = low.rolling(n).min()
    return -100 * (hh - close) / (hh - ll).replace(0, np.nan)


def _atr(high, low, close, n=14):
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _adx(high, low, close, n=14):
    up = high.diff()
    dn = -low.diff()
    plus_dm = np.where((up > dn) & (up > 0), up, 0.0)
    minus_dm = np.where((dn > up) & (dn > 0), dn, 0.0)
    tr = pd.concat([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1 / n, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=high.index).ewm(alpha=1 / n, adjust=False).mean() / atr.replace(0, np.nan)
    minus_di = 100 * pd.Series(minus_dm, index=high.index).ewm(alpha=1 / n, adjust=False).mean() / atr.replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, np.nan)
    return dx.ewm(alpha=1 / n, adjust=False).mean(), plus_di, minus_di


def _bollinger(close, n=20, k=2):
    mid = close.rolling(n).mean()
    sd = close.rolling(n).std()
    up, lo = mid + k * sd, mid - k * sd
    pctb = (close - lo) / (up - lo).replace(0, np.nan)
    return up, mid, lo, pctb


def _obv(close, vol):
    return (np.sign(close.diff()).fillna(0) * vol).cumsum()


def _last(x, digits=2):
    try:
        v = float(x.iloc[-1] if hasattr(x, "iloc") else x)
        return round(v, digits) if v == v and math.isfinite(v) else None
    except Exception:  # noqa: BLE001
        return None


# --------------------------- signal processing ---------------------------

def _sig(buy, sell):
    return "Buy" if buy else ("Sell" if sell else "Neutral")


def _rating_from(buy, sell, total):
    if not total:
        return "Neutral", 0.0
    score = (buy - sell) / total
    if score >= 0.5:
        label = "Strong Buy"
    elif score >= 0.15:
        label = "Buy"
    elif score <= -0.5:
        label = "Strong Sell"
    elif score <= -0.15:
        label = "Sell"
    else:
        label = "Neutral"
    return label, round(score, 3)


def currency_symbol(ticker):
    t = ticker.upper()
    if t.endswith((".NS", ".BO")):
        return "₹"
    return "$"


# --------------------------- main analysis ---------------------------

def analyze(ticker: str, name: str | None = None) -> dict | None:
    tkr = yf.Ticker(ticker)
    h = tkr.history(period="2y", auto_adjust=False)
    if h.empty or len(h) < 30:
        print(f"  ! not enough data for {ticker}", file=sys.stderr)
        return None
    close, high, low, vol = h["Close"], h["High"], h["Low"], h["Volume"]
    price = float(close.iloc[-1])
    prev = float(close.iloc[-2])
    chg = round((price / prev - 1) * 100, 2) if prev else 0.0
    cur = currency_symbol(ticker)

    # --- Moving averages: price above = bullish, below = bearish ---
    ma_defs = [("SMA", 10), ("SMA", 20), ("SMA", 30), ("SMA", 50), ("SMA", 100), ("SMA", 200),
               ("EMA", 10), ("EMA", 20), ("EMA", 50), ("EMA", 200)]
    ma_indicators, ma_buy, ma_sell = [], 0, 0
    for kind, n in ma_defs:
        if len(close) < n:
            continue
        val = _last(_sma(close, n) if kind == "SMA" else _ema(close, n))
        if val is None:
            continue
        buy, sell = price > val, price < val
        ma_buy += buy
        ma_sell += sell
        ma_indicators.append({"name": f"{kind} {n}", "value": val, "metric": kind.lower(),
                              "signal": "Bullish" if buy else ("Bearish" if sell else "Neutral"),
                              "note": f"price is {'above' if buy else 'below'} its {n}-day average — {'bullish' if buy else 'bearish'} for the {'short' if n <= 20 else 'medium' if n <= 50 else 'long'}-term trend"})

    # --- Oscillators ---
    osc_indicators, osc_buy, osc_sell = [], 0, 0

    rsi = _last(_rsi(close))
    if rsi is not None:
        buy, sell = rsi < 30, rsi > 70
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "RSI (14)", "value": rsi, "metric": "rsi", "signal": _sig(buy, sell),
                               "note": (f"{rsi:.0f} — oversold; selling may be overdone, watch for a bounce" if buy
                                        else f"{rsi:.0f} — overbought; risen fast, may pause or pull back" if sell
                                        else f"{rsi:.0f} — neutral momentum, no extreme")})

    ml, sl, _ = _macd(close)
    mv, sv = _last(ml, 3), _last(sl, 3)
    if mv is not None and sv is not None:
        buy, sell = mv > sv, mv < sv
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "MACD (12,26,9)", "value": mv, "metric": "macd", "signal": _sig(buy, sell),
                               "note": f"MACD line is {'above' if buy else 'below'} its signal line — momentum is {'improving (bullish)' if buy else 'deteriorating (bearish)'}"})

    k, dline = _stoch(high, low, close)
    kv = _last(k)
    if kv is not None:
        buy, sell = kv < 20, kv > 80
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "Stochastic %K (14,3)", "value": kv, "metric": "stochastic", "signal": _sig(buy, sell),
                               "note": ("closing near its recent lows — oversold" if buy
                                        else "closing near its recent highs — overbought" if sell
                                        else "closing in the middle of its recent range")})

    cci = _last(_cci(high, low, close))
    if cci is not None:
        buy, sell = cci < -100, cci > 100
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "CCI (20)", "value": cci, "metric": "cci", "signal": _sig(buy, sell),
                               "note": ("well below its average — oversold (or start of a down-move)" if buy
                                        else "well above its average — overbought (or a strong up-thrust)" if sell
                                        else "close to its recent average — no extreme")})

    wr = _last(_williams_r(high, low, close))
    if wr is not None:
        buy, sell = wr < -80, wr > -20
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "Williams %R (14)", "value": wr, "metric": "williams_r", "signal": _sig(buy, sell),
                               "note": ("near its recent lows — oversold" if buy
                                        else "near its recent highs — overbought" if sell
                                        else "mid-range — no extreme")})

    mom = _last(close - close.shift(10))
    if mom is not None:
        buy, sell = mom > 0, mom < 0
        osc_buy += buy; osc_sell += sell
        osc_indicators.append({"name": "Momentum (10)", "value": mom, "metric": "momentum", "signal": _sig(buy, sell),
                               "note": f"price is {'higher' if buy else 'lower'} than 10 days ago — {'upward' if buy else 'downward'} momentum"})

    # --- Trend strength (ADX) — reported, not a buy/sell vote ---
    adx_s, plus_di, minus_di = _adx(high, low, close)
    adx = _last(adx_s)
    trend_strength = "No trend"
    if adx is not None:
        trend_strength = "Strong" if adx >= 25 else ("Moderate" if adx >= 20 else "Weak")

    # --- Aggregate ratings ---
    ma_rating, _ = _rating_from(ma_buy, ma_sell, ma_buy + ma_sell + max(0, len(ma_indicators) - ma_buy - ma_sell))
    osc_rating, _ = _rating_from(osc_buy, osc_sell, len(osc_indicators))
    all_buy, all_sell, all_total = ma_buy + osc_buy, ma_sell + osc_sell, len(ma_indicators) + len(osc_indicators)
    overall_rating, overall_score = _rating_from(all_buy, all_sell, all_total)

    # --- Trend direction ---
    dma50, dma200 = _last(_sma(close, 50)), _last(_sma(close, 200))
    if dma50 and dma200:
        direction = "Uptrend" if price > dma50 > dma200 else ("Downtrend" if price < dma50 < dma200 else "Sideways")
    elif dma50:
        direction = "Up" if price > dma50 else "Down"
    else:
        direction = "Unclear"

    # --- Support / resistance via classic pivots + 52w range ---
    ph, pl, pc = float(high.iloc[-1]), float(low.iloc[-1]), float(close.iloc[-1])
    pivot = (ph + pl + pc) / 3
    levels = {
        "pivot": round(pivot, 2),
        "resistance": [round(2 * pivot - pl, 2), round(pivot + (ph - pl), 2)],
        "support": [round(2 * pivot - ph, 2), round(pivot - (ph - pl), 2)],
    }
    window = close.tail(252)
    lo52, hi52 = round(float(window.min()), 2), round(float(window.max()), 2)
    pos = round((price - lo52) / (hi52 - lo52) * 100, 1) if hi52 > lo52 else 50.0

    # --- Volatility ---
    atr = _last(_atr(high, low, close))
    atr_pct = round(atr / price * 100, 2) if atr else None
    _, _, _, pctb = _bollinger(close)
    bb = _last(pctb, 2)
    vol_label = "Normal"
    if atr_pct is not None:
        vol_label = "High" if atr_pct > 4 else ("Low" if atr_pct < 1.2 else "Normal")

    # --- Fundamentals (best effort) ---
    fundamentals = {}
    try:
        info = tkr.info or {}
        name = name or info.get("shortName") or ticker
        fundamentals = {k: info.get(k) for k in (
            "sector", "industry", "marketCap", "trailingPE", "forwardPE",
            "profitMargins", "revenueGrowth", "dividendYield", "beta") if info.get(k) is not None}
    except Exception:  # noqa: BLE001
        name = name or ticker

    # --- History for the dashboard's own clean chart (downsampled) ---
    tail = h.tail(180)
    sma50 = _sma(close, 50).tail(180)
    sma200 = _sma(close, 200).tail(180)
    history = [
        {"d": idx.strftime("%Y-%m-%d"), "c": round(float(c), 2),
         "m50": (round(float(a), 2) if a == a else None),
         "m200": (round(float(b), 2) if b == b else None)}
        for idx, c, a, b in zip(tail.index, tail["Close"], sma50, sma200)
    ]

    bull, bear = _cases(direction, mv, sv, rsi, adx, ma_buy, ma_sell, len(ma_indicators),
                        osc_indicators, pos, vol_label, price, dma50, dma200)
    analysis = {
        "the_read": _the_read(name, overall_rating, direction, trend_strength, adx, rsi, mv, sv,
                              dma50, dma200, price, pos, vol_label, atr_pct, cur),
        "bull_case": bull,
        "bear_case": bear,
        "what_would_flip": _what_would_flip(price, dma50, levels, cur),
        "fundamentals_read": _fundamentals_read(fundamentals, name, cur),
    }

    result = {
        "ticker": ticker,
        "name": name,
        "currency": cur,
        "as_of": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "price": round(price, 2),
        "change_pct": chg,
        "verdict": {
            "rating": overall_rating,
            "score": overall_score,
            "summary": _summary(name, overall_rating, direction, trend_strength, rsi, mv, sv, dma50, dma200, price, pos, cur),
        },
        "analysis": analysis,
        "signals": {
            "moving_averages": {"rating": ma_rating, "buy": ma_buy, "sell": ma_sell},
            "oscillators": {"rating": osc_rating, "buy": osc_buy, "sell": osc_sell},
        },
        "trend": {"direction": direction, "strength": trend_strength, "adx": adx,
                  "vs_50dma": ("above" if dma50 and price > dma50 else "below") if dma50 else None,
                  "vs_200dma": ("above" if dma200 and price > dma200 else "below") if dma200 else None},
        "indicators": {"moving_averages": ma_indicators, "oscillators": osc_indicators},
        "levels": levels,
        "range_52w": {"low": lo52, "high": hi52, "position_pct": pos},
        "volatility": {"atr": atr, "atr_pct": atr_pct, "bollinger_pctb": bb, "label": vol_label},
        "fundamentals": fundamentals,
        "history": history,
        "whats_new": "",   # enriched by the daily AI routine (news/what-changed)
        "news": [],
        "disclaimer": "Technical signals are rules-based and informational only — not financial advice.",
    }
    return result


def _money(v, cur="$"):
    try:
        v = float(v)
    except (TypeError, ValueError):
        return str(v)
    if v >= 1e12:
        return f"{cur}{v / 1e12:.2f}T"
    if v >= 1e9:
        return f"{cur}{v / 1e9:.1f}B"
    if v >= 1e6:
        return f"{cur}{v / 1e6:.0f}M"
    return f"{cur}{v:,.0f}"


def _the_read(name, rating, direction, strength, adx, rsi, macd, macd_sig, dma50, dma200, price, pos52, vol_label, atr_pct, cur):
    """A flowing, analyst-style paragraph a beginner can follow — the 'plain-English full read'."""
    s = []
    trend_txt = {"Uptrend": "in an uptrend", "Downtrend": "in a downtrend", "Sideways": "moving sideways",
                 "Up": "edging higher", "Down": "edging lower"}.get(direction, "in an unclear trend")
    s.append(f"{name} is {trend_txt}, and the full indicator suite reads {rating}.")
    if dma50 and dma200:
        if price > dma50 > dma200:
            s.append(f"Price sits above both its 50-day ({cur}{dma50:.0f}) and 200-day ({cur}{dma200:.0f}) averages, "
                     f"with the faster average above the slower one — the classic shape of a healthy uptrend.")
        elif price < dma50 < dma200:
            s.append(f"Price is below both its 50-day ({cur}{dma50:.0f}) and 200-day ({cur}{dma200:.0f}) averages — a textbook downtrend.")
        else:
            s.append(f"Price is caught between its 50-day ({cur}{dma50:.0f}) and 200-day ({cur}{dma200:.0f}) averages, "
                     f"so the trend is transitional and could break either way.")
    if adx is not None:
        s.append(f"Trend strength is {strength.lower()} (ADX {adx:.0f}) — "
                 f"{'moves here tend to persist' if adx >= 25 else 'the trend is weak, so expect choppier, range-bound action'}.")
    if rsi is not None and macd is not None and macd_sig is not None:
        mom = "improving" if macd > macd_sig else "deteriorating"
        rd = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
        s.append(f"Momentum is {mom} on MACD, and RSI sits at {rsi:.0f} ({rd}).")
    tail = f"It's trading in the {pos52:.0f}th percentile of its 52-week range"
    tail += f", and day-to-day volatility is {vol_label.lower()}" + (f" (~{atr_pct:.1f}% a day)." if atr_pct else ".")
    s.append(tail)
    return " ".join(s)


def _cases(direction, macd, macd_sig, rsi, adx, ma_buy, ma_sell, ma_total, osc_indicators, pos52, vol_label, price, dma50, dma200):
    """Turn the raw signals into a plain-English bull case (what supports it) and bear case (the risks)."""
    bull, bear = [], []
    if dma50 and dma200:
        if price > dma50 and price > dma200:
            bull.append("Trades above both its 50- and 200-day averages — a confirmed uptrend.")
        elif price < dma50 and price < dma200:
            bear.append("Trades below both its 50- and 200-day averages — a confirmed downtrend.")
        else:
            bear.append("Caught between its 50- and 200-day averages — no clear trend yet.")
    if ma_total:
        if ma_buy > ma_sell:
            bull.append(f"{ma_buy} of {ma_total} moving averages are bullish (price is above them).")
        elif ma_sell > ma_buy:
            bear.append(f"{ma_sell} of {ma_total} moving averages are bearish (price is below them).")
    if macd is not None and macd_sig is not None:
        if macd > macd_sig:
            bull.append("MACD momentum is positive — the bullish crossover is intact.")
        else:
            bear.append("MACD momentum is negative — momentum is fading.")
    if rsi is not None:
        if rsi < 30:
            bull.append(f"RSI is oversold ({rsi:.0f}) — selling may be overdone, so a bounce often follows.")
        elif rsi > 70:
            bear.append(f"RSI is overbought ({rsi:.0f}) — the run looks stretched and can pause or pull back.")
    if adx is not None and adx >= 25:
        if direction == "Uptrend":
            bull.append(f"Trend strength is strong (ADX {adx:.0f}) and pointing up — up-moves tend to persist.")
        elif direction == "Downtrend":
            bear.append(f"Trend strength is strong (ADX {adx:.0f}) and pointing down — down-moves tend to persist.")
    for i in osc_indicators:
        nm = i["name"].split(" (")[0]
        if nm in ("Stochastic %K", "CCI", "Williams %R"):
            if i["signal"] == "Buy":
                bull.append(f"{nm} is oversold — a short-term bounce signal.")
            elif i["signal"] == "Sell":
                bear.append(f"{nm} is overbought — a short-term caution signal.")
    if pos52 >= 80:
        bull.append("Trading near its 52-week high — strong relative strength.")
    elif pos52 <= 20:
        bear.append("Trading near its 52-week low — weak, though it may be oversold value.")
    if vol_label == "High":
        bear.append("Volatility is high — expect larger swings both ways, so size positions carefully.")
    return bull[:6], bear[:6]


def _what_would_flip(price, dma50, levels, cur):
    """The concrete levels a beginner should watch to know if the read is changing."""
    parts = []
    if dma50:
        if price < dma50:
            parts.append(f"A daily close back above the 50-day average (~{cur}{dma50:.0f}) would be the first sign the downtrend is turning up.")
        else:
            parts.append(f"A daily close below the 50-day average (~{cur}{dma50:.0f}) would warn the uptrend is stalling.")
    res = (levels or {}).get("resistance") or []
    sup = (levels or {}).get("support") or []
    if res:
        parts.append(f"First resistance to clear overhead: {cur}{res[0]:.0f}.")
    if sup:
        parts.append(f"First support that needs to hold: {cur}{sup[0]:.0f}.")
    return " ".join(parts)


def _fundamentals_read(f, name, cur):
    """Explain the fundamentals in words, not just numbers."""
    if not f:
        return ""
    sec = f.get("sector"); pe = f.get("trailingPE"); fpe = f.get("forwardPE")
    growth = f.get("revenueGrowth"); margin = f.get("profitMargins")
    beta = f.get("beta"); dy = f.get("dividendYield"); mc = f.get("marketCap")
    bits = []
    if mc:
        size = ("a mega-cap" if mc >= 2e11 else "a large-cap" if mc >= 1e10 else "a mid-cap" if mc >= 2e9 else "a small-cap")
        bits.append(f"{name} is {size} company{(' in ' + sec) if sec else ''}, worth about {_money(mc, cur)}.")
    if pe:
        lvl = ("expensive — investors are paying up for strong expected growth" if pe >= 35
               else "on the rich side" if pe >= 25 else "moderate" if pe >= 15
               else "low, which can signal value or a troubled business")
        line = f"It trades at a P/E of {pe:.0f} ({lvl})"
        if fpe and fpe < pe:
            line += f"; the lower forward P/E of {fpe:.0f} suggests profits are expected to grow"
        elif fpe and fpe > pe:
            line += f"; the higher forward P/E of {fpe:.0f} suggests profits are expected to fall"
        bits.append(line + ".")
    if growth is not None:
        g = growth * 100
        line = f"Revenue is {'growing' if g >= 0 else 'shrinking'} about {abs(g):.0f}% a year"
        if margin is not None:
            line += f", and it keeps roughly {margin * 100:.0f}¢ of every sales dollar as profit"
        bits.append(line + ".")
    elif margin is not None:
        bits.append(f"It keeps roughly {margin * 100:.0f}¢ of every sales dollar as profit.")
    if beta is not None:
        bdesc = ("about as volatile as the market" if 0.8 <= beta <= 1.2
                 else "more volatile than the market" if beta > 1.2 else "steadier than the market")
        bits.append(f"With a beta of {beta:.2f}, it's {bdesc}.")
    if dy:
        # yfinance is inconsistent: older builds return a fraction (0.0044), newer ones a percent (0.44).
        dy_pct = dy * 100 if dy < 0.2 else dy
        bits.append(f"It pays a dividend yielding {dy_pct:.1f}%.")
    return " ".join(bits)


def _summary(name, rating, direction, strength, rsi, macd, macd_sig, dma50, dma200, price, pos52, cur):
    bits = [f"{name} is rated **{rating}** on the technical suite."]
    if dma50 and dma200:
        rel = ("above both its 50- and 200-day averages (a healthy uptrend)" if price > dma50 and price > dma200
               else "below both its 50- and 200-day averages (a downtrend)" if price < dma50 and price < dma200
               else "between its 50- and 200-day averages (mixed / transitional)")
        bits.append(f"Price is {rel}.")
    if rsi is not None:
        r = "oversold" if rsi < 30 else "overbought" if rsi > 70 else "neutral"
        bits.append(f"Momentum is {r} (RSI {rsi:.0f}).")
    if macd is not None and macd_sig is not None:
        bits.append(f"MACD is {'bullish' if macd > macd_sig else 'bearish'}.")
    bits.append(f"Trend strength is {strength.lower()}; it sits at the {pos52:.0f}th percentile of its 52-week range.")
    return " ".join(bits)


# --------------------------- io ---------------------------

def _safe_name(ticker):
    return ticker.upper().replace("/", "_").replace("^", "_")


def _atomic_write(path: pathlib.Path, text: str) -> None:
    """Write via tmp + rename so readers (browser, other processes) never see partial JSON."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text)
    os.replace(tmp, path)


def save(result: dict) -> pathlib.Path:
    path = STOCKS / f"{_safe_name(result['ticker'])}.json"
    _atomic_write(path, json.dumps(result, indent=2, default=str))
    return path


def build_index():
    favs = set()
    if yaml is not None:
        try:
            for f in (yaml.safe_load((ROOT / "config/favorites.yml").read_text()) or {}).get("favorites", []):
                favs.add(f["ticker"])
        except Exception:  # noqa: BLE001
            pass
    rows = []
    for p in sorted(STOCKS.glob("*.json")):
        if p.name == "index.json":
            continue
        try:
            d = json.loads(p.read_text())
            v = d.get("verdict", {})
            osc = [i for i in d.get("indicators", {}).get("oscillators", []) if i["name"].startswith("RSI")]
            rows.append({
                "ticker": d["ticker"], "name": d.get("name"),
                "rating": v.get("rating"), "score": v.get("score"),
                "change_pct": d.get("change_pct"), "price": d.get("price"),
                "currency": d.get("currency", "$"),
                "favorite": d["ticker"] in favs,
                "trend": d.get("trend", {}).get("direction"),
                "rsi": (osc[0]["value"] if osc else None),
                "as_of": d.get("as_of"),
                "one_liner": (v.get("summary", "").split(". ")[1] if ". " in v.get("summary", "") else v.get("summary", ""))[:120],
            })
        except Exception:  # noqa: BLE001
            pass
    rows.sort(key=lambda r: (not r["favorite"], -(r.get("score") or 0)))
    _atomic_write(STOCKS / "index.json", json.dumps(rows, indent=2))
    return rows


def _all_tickers():
    if yaml is None:
        return []
    tickers = []
    wl = yaml.safe_load((ROOT / "config/watchlist.yml").read_text()) or {}
    for group in wl.values():
        for row in group or []:
            tickers.append((row["ticker"], row.get("name")))
    favs = (yaml.safe_load((ROOT / "config/favorites.yml").read_text()) or {}).get("favorites", [])
    for f in favs:
        tickers.append((f["ticker"], f.get("name")))
    seen, out = set(), []
    for t, n in tickers:
        if t not in seen:
            seen.add(t)
            out.append((t, n))
    return out


def main(argv):
    if not argv:
        print(__doc__)
        return
    if argv[0] == "--all":
        targets = _all_tickers()
    else:
        targets = [(t, None) for t in argv]
    for ticker, name in targets:
        print(f"Analyzing {ticker}...")
        res = analyze(ticker, name)
        if res:
            p = save(res)
            v = res["verdict"]
            print(f"  {res['name']}: {v['rating']} (score {v['score']}) -> {p.relative_to(ROOT)}")
    build_index()
    print("Updated dashboard/stocks/index.json")


if __name__ == "__main__":
    main(sys.argv[1:])
