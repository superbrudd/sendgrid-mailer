#!/usr/bin/env python3
"""
Simple local server for SendGrid Bulk Mailer.

Serves sendgrid-mailer.html, proxies POST /send to the SendGrid API,
and provides GET/POST /data for persistent local file storage.

Data is saved to mailer_data/ next to this script:
    mailer_data/config.json
    mailer_data/campaigns.json
    mailer_data/history.json
    mailer_data/draft.json

Usage:
    python mailer_server.py
    python mailer_server.py --port 8766

Then open: http://localhost:8766
"""

import argparse
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

PORT = 8766
HTML_FILE  = Path(__file__).parent / "sendgrid-mailer.html"
DATA_DIR   = Path(__file__).parent / "mailer_data"
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"

DATA_KEYS  = ("config", "campaigns", "history", "draft")
EMPTY      = {"config": {}, "campaigns": [], "history": [], "draft": {}}


def data_file(key):
    return DATA_DIR / f"{key}.json"


def read_all_data():
    result = {}
    for key in DATA_KEYS:
        path = data_file(key)
        try:
            result[key] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else EMPTY[key]
        except Exception:
            result[key] = EMPTY[key]
    return result


def write_data(key, value):
    DATA_DIR.mkdir(exist_ok=True)
    data_file(key).write_text(json.dumps(value, indent=2, ensure_ascii=False), encoding="utf-8")


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/sendgrid-mailer.html"):
            self._serve_html()
        elif self.path == "/data":
            self._get_data()
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        if self.path == "/send":
            self._proxy_send()
        elif self.path == "/data":
            self._post_data()
        else:
            self._send(404, "text/plain", b"Not found")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ── handlers ─────────────────────────────────────────────────────────────

    def _serve_html(self):
        try:
            body = HTML_FILE.read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
        except FileNotFoundError:
            self._send(404, "text/plain", b"sendgrid-mailer.html not found")

    def _get_data(self):
        try:
            data = read_all_data()
            self._send(200, "application/json", json.dumps(data).encode())
        except Exception as e:
            self._send(500, "application/json", json.dumps({"error": str(e)}).encode())

    def _post_data(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            body   = json.loads(self.rfile.read(length))
            key    = body.get("key")
            value  = body.get("value")
            if key not in DATA_KEYS:
                self._send(400, "application/json", b'{"error":"unknown key"}')
                return
            write_data(key, value)
            self._send(200, "application/json", b'{"ok":true}')
        except Exception as e:
            self._send(500, "application/json", json.dumps({"error": str(e)}).encode())

    def _proxy_send(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        auth   = self.headers.get("Authorization", "")

        req = urllib.request.Request(
            SENDGRID_URL,
            data=body,
            method="POST",
            headers={
                "Authorization": auth,
                "Content-Type":  "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req) as resp:
                self._send(resp.status, "application/json", resp.read())
        except urllib.error.HTTPError as e:
            self._send(e.code, "application/json", e.read())
        except urllib.error.URLError as e:
            msg = json.dumps({"errors": [{"message": str(e.reason)}]}).encode()
            self._send(502, "application/json", msg)

    # ── helpers ───────────────────────────────────────────────────────────────

    def _send(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")

    def log_message(self, fmt, *args):
        print(f"  {self.address_string()} {fmt % args}")


def main():
    parser = argparse.ArgumentParser(description="SendGrid Mailer local server")
    parser.add_argument("--port", type=int, default=PORT)
    args = parser.parse_args()

    DATA_DIR.mkdir(exist_ok=True)
    print(f"Data folder: {DATA_DIR.resolve()}")

    server = HTTPServer(("localhost", args.port), Handler)
    print(f"SendGrid Mailer running at http://localhost:{args.port}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
