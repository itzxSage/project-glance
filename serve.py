#!/usr/bin/env python3
"""
serve.py — stdlib-only static server for Project Glance.

Serves the SPA plus /data/*.json for the frontend to poll, and exposes
POST /api/notes so the Work-Together "Save note" button persists locally.

Run:
    python3 serve.py          # http://127.0.0.1:8000
    python3 serve.py 9000     # custom port
"""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
DOCS = [".html", ".css", ".js", ".json", ".svg", ".png", ".ico", ".txt"]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/data/"):
            f = DATA_DIR / self.path[len("/data/"):]
            if not f.is_file():
                self.send_error(404)
                return
            self._send_file(f)
            return
        # single-page app routing fallback
        if self.path in ("/", "/index.html") or self.path.startswith("/#"):
            self._send_file(ROOT / "index.html")
            return
        if self.path.startswith("/"):
            f = ROOT / self.path.lstrip("/")
            if f.is_file() and f.suffix in DOCS:
                self._send_file(f)
                return
        self.send_error(404)

    def do_POST(self):
        if self.path == "/api/notes":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length) or b"{}")
            note = body.get("note", "").strip()
            if not note:
                self._send_json(400, {"error": "empty note"})
                return
            notes_path = ROOT / "data" / "notes.json"
            notes = []
            if notes_path.exists():
                try:
                    notes = json.loads(notes_path.read_text())
                except Exception:
                    notes = []
            notes.append(note)
            notes_path.write_text(json.dumps(notes, indent=2) + "\n", encoding="utf-8")
            self._send_json(200, {"ok": True, "note": note})
            return
        self.send_error(404)

    def _send_file(self, f):
        data = f.read_bytes()
        ctype = {
            ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
            ".json": "application/json", ".svg": "image/svg+xml", ".png": "image/png",
            ".ico": "image/x-icon", ".txt": "text/plain",
        }.get(f.suffix, "application/octet-stream")
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_json(self, status, obj):
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        sys.stderr.write("[Glance] %s\n" % (format % args))


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[Glance] serving at http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()
