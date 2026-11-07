#!/usr/bin/env python3
"""
StudySapiens — local preview server + tiny contact API (optional).

Usage:
    python3 server.py            → serves ./site at http://localhost:8000
    python3 server.py 8080       → custom port

The /api/contact endpoint lets you receive form submissions without any
third-party service when self-hosting (messages are appended to messages.csv
and printed to the console). Wire the site's forms to it by changing the
form's `data-mailto` to a normal fetch POST if you want (see README).
"""
import http.server, socketserver, sys, json, csv, os, datetime

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "site")
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def end_headers(self):
        # simple security headers
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "SAMEORIGIN")
        self.send_header("Referrer-Policy", "strict-origin-when-cross-origin")
        # report-only CSP mirrors production _headers so console warnings can be
        # reviewed locally before ever enforcing
        self.send_header("Content-Security-Policy-Report-Only",
            "default-src 'self'; script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; "
            "connect-src 'self'; manifest-src 'self'; worker-src 'self'; "
            "frame-ancestors 'self'; base-uri 'self'; form-action 'self' mailto:; "
            "object-src 'none'")
        super().end_headers()

    def send_error(self, code, message=None, explain=None):
        # serve the branded 404 page for missing routes (like Netlify/CF Pages do)
        if code == 404:
            p404 = os.path.join(ROOT, "404.html")
            if os.path.exists(p404):
                body = open(p404, "rb").read()
                self.send_response(404)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
        super().send_error(code, message, explain)

    def do_POST(self):
        if self.path == "/api/contact":
            try:
                length = int(self.headers.get("Content-Length", 0))
                data = json.loads(self.rfile.read(length) or b"{}")
                row = {"time": datetime.datetime.now().isoformat(timespec="seconds"), **data}
                path = os.path.join(os.path.dirname(ROOT), "messages.csv")
                new = not os.path.exists(path)
                with open(path, "a", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=row.keys())
                    if new: w.writeheader()
                    w.writerow(row)
                print("📩 New message:", row)
                body = json.dumps({"ok": True}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except Exception as e:
                self.send_response(400); self.end_headers()
        else:
            self.send_response(404); self.end_headers()

    def log_message(self, fmt, *args):
        print("  ", fmt % args)

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 StudySapiens running → http://localhost:{PORT}")
        print(f"   Serving: {ROOT}")
        httpd.serve_forever()
