#!/usr/bin/env python3
"""
Simple local server for SendGrid Bulk Mailer.

Serves sendgrid-mailer.html and proxies POST /send to the SendGrid API
so the browser isn't blocked by CORS when making direct API calls.

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
HTML_FILE = Path(__file__).parent / "sendgrid-mailer.html"
SENDGRID_URL = "https://api.sendgrid.com/v3/mail/send"


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path in ("/", "/sendgrid-mailer.html"):
            self._serve_html()
        else:
            self._send(404, "text/plain", b"Not found")

    def do_POST(self):
        if self.path == "/send":
            self._proxy_send()
        else:
            self._send(404, "text/plain", b"Not found")

    def do_OPTIONS(self):
        # Pre-flight CORS request
        self.send_response(204)
        self._cors_headers()
        self.end_headers()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _serve_html(self):
        try:
            body = HTML_FILE.read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
        except FileNotFoundError:
            self._send(404, "text/plain", b"sendgrid-mailer.html not found")

    def _proxy_send(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        auth   = self.headers.get("Authorization", "")

        req = urllib.request.Request(
            SENDGRID_URL,
            data=body,
            method="POST",
            headers={
                "Authorization":  auth,
                "Content-Type":   "application/json",
            },
        )

        try:
            with urllib.request.urlopen(req) as resp:
                self._send(resp.status, "application/json", resp.read())
        except urllib.error.HTTPError as e:
            error_body = e.read()
            self._send(e.code, "application/json", error_body)
        except urllib.error.URLError as e:
            msg = json.dumps({"errors": [{"message": str(e.reason)}]}).encode()
            self._send(502, "application/json", msg)

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

    server = HTTPServer(("localhost", args.port), Handler)
    print(f"SendGrid Mailer running at http://localhost:{args.port}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
