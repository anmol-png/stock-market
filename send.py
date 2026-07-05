#!/usr/bin/env python3
"""Render the daily two-pillar brief to a clean email and send it via Gmail SMTP.

Reads both pillars — output/world-latest.json (decoded World news) and output/brief-latest.json
(Markets) — and builds a SHORT, scannable, mobile-friendly email: the day's must-know items from
each pillar, with the full decoded depth one tap away on the dashboard. Either pillar can be
missing; the email renders whatever is available.

Run:  python send.py
Env:  GMAIL_ADDRESS, GMAIL_APP_PASSWORD, EMAIL_TO, DASHBOARD_URL
"""
from __future__ import annotations

import datetime as dt
import html
import json
import os
import pathlib
import smtplib
import ssl
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

ROOT = pathlib.Path(__file__).resolve().parent
WORLD = ROOT / "output" / "world-latest.json"
BRIEF = ROOT / "output" / "brief-latest.json"

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "").strip()
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "").strip()
EMAIL_TO = os.getenv("EMAIL_TO", GMAIL_ADDRESS).strip()
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "").strip()

CAT_EMOJI = {"geopolitics": "🌍", "economy": "💵", "technology": "⚙️", "science": "🔬",
             "health": "🩺", "climate": "🌱", "india": "🇮🇳"}
CAT_COLOR = {"geopolitics": "#c0362c", "economy": "#0a8a3a", "technology": "#7c3aed",
             "science": "#0d9488", "health": "#db2777", "climate": "#3f9d5f", "india": "#d97706"}


def e(x) -> str:
    return html.escape(str(x)) if x is not None else ""


def color_for(pct) -> str:
    try:
        return "#0a8a3a" if float(pct) >= 0 else "#c0362c"
    except (TypeError, ValueError):
        return "#444"


def sign(pct) -> str:
    try:
        return f"{'+' if float(pct) >= 0 else ''}{float(pct):.2f}%"
    except (TypeError, ValueError):
        return "—"


def _label(text: str) -> str:
    return (f'<div style="font-size:12px;font-weight:700;color:#0f172a;text-transform:uppercase;'
            f'letter-spacing:.5px;margin:22px 0 6px;">{text}</div>')


def _dash_link(anchor: str, text: str) -> str:
    if not DASHBOARD_URL:
        return ""
    sep = "" if DASHBOARD_URL.endswith("#") else "#"
    return (f'<div style="margin:6px 0 2px;font-size:13px;">'
            f'<a href="{e(DASHBOARD_URL)}{sep}{anchor}" style="color:#2b6cb0;font-weight:600;">{text} →</a></div>')


# ------------------------------- WORLD pillar -------------------------------

def render_world(world: dict) -> str:
    if not world:
        return ""
    out = [_label("🌍 World — what you shouldn't miss")]
    if world.get("the_big_picture"):
        out.append(f'<div style="font-size:14px;color:#333;background:#f1f5ff;border-left:3px solid #2b6cb0;'
                   f'padding:10px 12px;border-radius:6px;margin-bottom:8px;">{e(world["the_big_picture"])}</div>')
    rows = ""
    for s in (world.get("stories") or [])[:5]:
        cat = str(s.get("category", ""))
        emoji = CAT_EMOJI.get(cat, "•")
        col = CAT_COLOR.get(cat, "#555")
        rows += f"""
        <tr><td style="padding:9px 0;border-bottom:1px solid #eee;">
          <div style="font-weight:700;color:#111;font-size:14.5px;">
            {e(s.get('rank',''))}. {e(s.get('title'))}
            <span style="font-weight:700;color:{col};font-size:11px;">&nbsp;{emoji} {e(cat.title())}</span>
          </div>
          <div style="color:#333;font-size:13.5px;margin-top:2px;"><b>Why it matters:</b> {e(s.get('why_it_matters'))}</div>
        </td></tr>"""
    out.append(f'<table width="100%">{rows or "<tr><td style=color:#888>No world stories today.</td></tr>"}</table>')
    out.append(_dash_link("world", "Read the full decoded analysis"))
    return "".join(out)


# ------------------------------- MARKETS pillar -------------------------------

def render_markets(brief: dict) -> str:
    if not brief:
        return ""
    out = [_label("📈 Markets — today's signal")]
    if brief.get("headline"):
        out.append(f'<div style="font-size:14px;color:#333;margin-bottom:6px;">{e(brief["headline"])}</div>')

    watch_rows = ""
    for item in (brief.get("what_to_watch") or [])[:4]:
        tick = ", ".join(item.get("tickers", []) or [])
        watch_rows += f"""
        <tr><td style="padding:8px 0;border-bottom:1px solid #eee;">
          <div style="font-weight:700;color:#111;font-size:14px;">#{e(item.get('rank',''))} {e(item.get('title'))}
            <span style="font-weight:400;color:#888;font-size:11px;">[{e(item.get('market'))}{(' · '+e(tick)) if tick else ''}]</span></div>
          <div style="color:#333;font-size:13px;margin-top:2px;">{e(item.get('gist') or item.get('why'))}</div>
        </td></tr>"""
    if watch_rows:
        out.append('<div style="font-size:12px;font-weight:700;color:#334;margin:10px 0 2px;">▲ Don\'t miss</div>')
        out.append(f'<table width="100%">{watch_rows}</table>')

    fav_rows = ""
    for f in (brief.get("favorites") or []):
        fav_rows += (
            f'<tr><td style="padding:6px 0;font-size:13px;color:#333;border-bottom:1px solid #f0f0f0;">'
            f'<b style="color:#111;">{e(f.get("name"))}</b> '
            f'<span style="color:#888;">{e(f.get("ticker"))}</span> '
            f'<span style="color:{color_for(f.get("change_pct"))};font-weight:700;">{sign(f.get("change_pct"))}</span><br>'
            f'<span style="color:#444;">{e(f.get("whats_new"))}</span></td></tr>'
        )
    if fav_rows:
        out.append('<div style="font-size:12px;font-weight:700;color:#334;margin:12px 0 2px;">★ Your stocks — what changed</div>')
        out.append(f'<table width="100%">{fav_rows}</table>')

    out.append(_dash_link("markets", "Open full technical analysis + every metric explained"))
    return "".join(out)


def render(world: dict | None, brief: dict | None) -> str:
    date = e((world or {}).get("date") or (brief or {}).get("date") or dt.date.today().isoformat())
    hero = e((world or {}).get("headline") or (brief or {}).get("headline") or "Your daily intelligence brief")
    disclaimer = e((world or {}).get("disclaimer")
                   or (brief or {}).get("disclaimer")
                   or "For information only. Not financial advice. Decoded from public reporting; verify before acting.")

    body = render_world(world) + render_markets(brief)
    return f"""<!doctype html><html><body style="margin:0;background:#f4f5f7;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:16px 0;"><tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;overflow:hidden;">
      <tr><td style="background:#0f172a;padding:18px 22px;">
        <div style="color:#fff;font-size:13px;letter-spacing:1px;text-transform:uppercase;opacity:.7;">🧭 Daily Intelligence · {date}</div>
        <div style="color:#fff;font-size:19px;font-weight:700;margin-top:4px;line-height:1.35;">{hero}</div>
      </td></tr>
      <tr><td style="padding:6px 22px 18px;">
        {body}
      </td></tr>
      <tr><td style="padding:14px 22px;background:#f8fafc;border-top:1px solid #eee;">
        <div style="font-size:11px;color:#999;">{disclaimer}</div>
      </td></tr>
    </table></td></tr></table></body></html>"""


def _load(path: pathlib.Path) -> dict | None:
    return json.loads(path.read_text()) if path.exists() else None


def main() -> None:
    world, brief = _load(WORLD), _load(BRIEF)
    if not (world or brief):
        print("No briefs found (world-latest.json / brief-latest.json). Run the analysis steps first.", file=sys.stderr)
        sys.exit(1)
    if not (GMAIL_ADDRESS and GMAIL_APP_PASSWORD and EMAIL_TO):
        print("Missing GMAIL_ADDRESS / GMAIL_APP_PASSWORD / EMAIL_TO in environment (.env).", file=sys.stderr)
        sys.exit(1)

    body = render(world, brief)
    date = (world or brief).get("date", dt.date.today().isoformat())
    hero = (world or {}).get("headline") or (brief or {}).get("headline") or ""
    subject = f"🧭 Daily Intelligence · {date} — {hero}"[:150]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = EMAIL_TO
    msg.attach(MIMEText("Your daily World + Markets brief is best viewed as HTML.", "plain"))
    msg.attach(MIMEText(body, "html"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as server:
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_ADDRESS, [EMAIL_TO], msg.as_string())
    print(f"Sent brief to {EMAIL_TO}.")


if __name__ == "__main__":
    main()
