#!/usr/bin/env python3
"""Local dashboard server with live stock lookup + on-demand refresh.

Serves the dashboard/ folder AND exposes:
    /api/analyze?ticker=XYZ  — live in-depth technical analysis for ANY ticker on demand
    /api/refresh             — recompute the whole tracked universe (fresh prices/verdicts)
    /api/refresh_news        — re-pull the world RSS feeds and rebuild dashboard/headlines.json

Threaded, so a long refresh never blocks live lookups. A lock serializes index writes;
the refresh endpoints reject concurrent duplicates instead of stacking runs.

Run:  python server.py        # then open http://localhost:8000
"""
from __future__ import annotations

import http.server
import json
import pathlib
import threading
import urllib.parse

import analyze_stock
import build_dashboard
import fetch_world

ROOT = pathlib.Path(__file__).resolve().parent
DASH = ROOT / "dashboard"
PORT = 8000

INDEX_LOCK = threading.Lock()    # serializes save()+build_index() across threads
STOCKS_LOCK = threading.Lock()   # one /api/refresh at a time
NEWS_LOCK = threading.Lock()     # one /api/refresh_news at a time


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DASH), **kwargs)

    def do_GET(self):  # noqa: N802
        if self.path.startswith("/api/analyze"):
            self.handle_analyze()
            return
        if self.path.startswith("/api/refresh_news"):
            self.handle_refresh_news()
            return
        if self.path.startswith("/api/refresh"):
            self.handle_refresh()
            return
        super().do_GET()

    def _send_json(self, obj, status=200):
        body = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def handle_analyze(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        ticker = (params.get("ticker") or [""])[0].strip()
        if not ticker:
            self.send_error(400, "ticker required")
            return
        try:
            res = analyze_stock.analyze(ticker)
            if not res:
                self.send_error(404, "no data for ticker")
                return
            with INDEX_LOCK:
                analyze_stock.save(res)
                analyze_stock.build_index()
            self._send_json(res)
        except Exception as exc:  # noqa: BLE001
            self.send_error(500, str(exc))

    def handle_refresh(self):
        """Recompute live technical analysis for every tracked ticker (fresh prices/verdicts)."""
        if not STOCKS_LOCK.acquire(blocking=False):
            self._send_json({"ok": False, "busy": True})
            return
        try:
            n = 0
            for ticker, name in analyze_stock._all_tickers():
                res = analyze_stock.analyze(ticker, name)
                if res:
                    with INDEX_LOCK:
                        analyze_stock.save(res)
                    n += 1
            with INDEX_LOCK:
                analyze_stock.build_index()
            self._send_json({"ok": True, "refreshed": n})
        except Exception as exc:  # noqa: BLE001
            self.send_error(500, str(exc))
        finally:
            STOCKS_LOCK.release()

    def handle_refresh_news(self):
        """Re-pull the world RSS feeds and rebuild the Latest-headlines strip."""
        if not NEWS_LOCK.acquire(blocking=False):
            self._send_json({"ok": False, "busy": True})
            return
        try:
            fetch_world.main()
            n = build_dashboard.build_headlines()
            self._send_json({"ok": True, "headlines": n})
        except Exception as exc:  # noqa: BLE001
            self.send_error(500, str(exc))
        finally:
            NEWS_LOCK.release()

    def log_message(self, *args):  # quiet
        pass


if __name__ == "__main__":
    server = http.server.ThreadingHTTPServer(("", PORT), Handler)
    server.daemon_threads = True
    print(f"Dashboard + live lookup on http://localhost:{PORT}  (Ctrl-C to stop)")
    server.serve_forever()
