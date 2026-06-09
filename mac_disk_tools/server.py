# -*- coding: utf-8 -*-
"""Local HTTP server for Mac Disk Tools."""

from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .actions import attach_delete_policy, move_to_trash, open_in_finder
from .config import PORT
from .scanner import browse_dir, fmt, get_disk_info, scan_paths
from .ui import HTML


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send_json_or_text(200, "text/html; charset=utf-8", HTML.encode())
        elif path == "/api/scan":
            self._handle_scan()
        elif path == "/api/browse":
            self._handle_browse()
        else:
            self._send_json_or_text(404, "text/plain", b"Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path).path
        if parsed_path == "/api/open":
            body = self._read_json_body()
            ok, msg = open_in_finder(body.get("path", ""))
            self._send_json({"success": ok, "message": msg})
        elif parsed_path == "/api/delete":
            body = self._read_json_body()
            ok, msg = move_to_trash(body.get("path", ""))
            self._send_json({"success": ok, "message": msg})
        else:
            self._send_json_or_text(404, "text/plain", b"Not Found")

    def _handle_scan(self):
        disk = get_disk_info()
        pct = round(disk["used"] / max(disk["total"], 1) * 100, 1)
        items = [attach_delete_policy(item) for item in scan_paths()]
        self._send_json({
            "disk": disk,
            "disk_formatted": {
                "total": fmt(disk["total"], "en"),
                "used": fmt(disk["used"], "en"),
                "available": fmt(disk["available"], "en"),
                "percent": pct,
            },
            "items": items,
        })

    def _handle_browse(self):
        query = parse_qs(urlparse(self.path).query)
        path = query.get("path", [""])[0]
        if not path:
            self._send_json({"error": "Missing path parameter"})
            return

        items, err = browse_dir(path)
        if err:
            self._send_json({"error": err, "items": []})
            return

        max_size = max((i["size"] for i in items if i["size"]), default=1)
        for item in items:
            item["pct"] = round(item["size"] / max_size * 100) if item["size"] else 0
            attach_delete_policy(item)

        self._send_json({"items": items, "path": path})

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        return json.loads(self.rfile.read(length))

    def _send_json(self, payload, code=200):
        self._send_json_or_text(
            code,
            "application/json; charset=utf-8",
            json.dumps(payload).encode(),
        )

    def _send_json_or_text(self, code, content_type, body):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *_):
        pass


def run(open_browser=True):
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{PORT}"
    print(f"✅ 磁盘分析工具已启动：{url}")
    if open_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 已停止")


def main():
    run(open_browser=True)
