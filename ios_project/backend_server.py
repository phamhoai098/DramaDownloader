"""
backend_server.py
~~~~~~~~~~~~~~~~~
High-performance REST API Server for DramaDownloader iOS App.
Built using Python standard libraries (no external pip dependencies needed).
Provides endpoints:
- GET /api/platforms
- GET /api/catalog?platform=dramabox&lang=vi&page=1&q=
- GET /api/inspect?url=<link_or_id>&platform=
- GET /api/video_url?url=<episode_url>&platform=
"""

import sys
import os
import json
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add root folder to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import drama_downloader as dd
from drama_downloader.models import Series, Episode, CatalogItem

class DramaAPIHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        try:
            if path == '/api/platforms':
                plats = [
                    {"id": p.platform_id, "name": p.display_name}
                    for p in dd.get_all_platforms()
                ]
                self._send_json(200, {"platforms": plats})

            elif path == '/api/categories':
                platform_id = query.get('platform', ['dramabox'])[0]
                lang = query.get('lang', ['vi'])[0]
                plat = dd.get_platform(platform_id)
                cats = plat.get_categories(language=lang) if plat else [{'id': '0', 'name': '🔥 Tất Cả'}]
                self._send_json(200, {"categories": cats})

            elif path == '/api/catalog':
                platform_id = query.get('platform', ['dramabox'])[0]
                lang = query.get('lang', ['vi'])[0]
                page = int(query.get('page', ['1'])[0])
                search_q = query.get('q', [''])[0] or None
                cat_id = query.get('category', [''])[0] or None

                plat = dd.get_platform(platform_id)
                if not plat:
                    self._send_json(404, {"error": f"Platform '{platform_id}' not found"})
                    return

                res = plat.get_catalog(page=page, query=search_q, category=cat_id, language=lang)
                items = [it.to_dict() for it in (res.items if res else [])]
                total = res.total if res else 0
                self._send_json(200, {"items": items, "total": total})

            elif path == '/api/inspect':
                target = query.get('url', [''])[0]
                hint = query.get('platform', [None])[0]
                if not target:
                    self._send_json(400, {"error": "Missing 'url' parameter"})
                    return

                series = dd.load_series(target, platform_hint=hint)
                self._send_json(200, series.to_dict())

            else:
                self._send_json(404, {"error": "Endpoint not found"})

        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def log_message(self, format, *args):
        sys.stderr.write(f"[{self.log_date_time_string()}] {format % args}\n")

def run_server(port: int = None):
    if port is None:
        port = int(os.environ.get('PORT', 8000))
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, DramaAPIHandler)
    print("=====================================================")
    print(f"[START] DramaDownloader iOS Backend API running on port {port}")
    print(f"Local Access:   http://localhost:{port}")
    print(f"LAN/Wi-Fi URL:  http://<YOUR_PC_IP>:{port}")
    print("=====================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

if __name__ == '__main__':
    run_server()
