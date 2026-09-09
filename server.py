"""
LeetCode Amazon Interview Explorer Server
Wires together the LeetCode dataset (data/experiences.json) and frontend UI (ui/).
"""

import http.server
import json
import os
import socketserver
import sys
import threading
import urllib.parse
import webbrowser

PORT = 5173
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(BASE_DIR, "ui")
DATA_FILE = os.path.join(BASE_DIR, "data", "experiences.json")

class LeetCodeHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=UI_DIR, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # Handle API endpoints
        if path == "/api/experiences":
            try:
                content = b"[]"
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, "rb") as f:
                        content = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass
            except Exception:
                pass
            return

        if path == "/api/status":
            try:
                count = 0
                if os.path.exists(DATA_FILE):
                    try:
                        with open(DATA_FILE, "r", encoding="utf-8") as f:
                            count = len(json.load(f))
                    except Exception:
                        pass
                content = json.dumps({
                    "status": "online",
                    "total_experiences": count,
                    "data_path": DATA_FILE,
                    "ui_path": UI_DIR
                }).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(content)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(content)
            except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
                pass
            except Exception:
                pass
            return

        # Serve static UI files
        try:
            return super().do_GET()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def handle(self):
        try:
            super().handle()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def finish(self):
        try:
            super().finish()
        except (ConnectionResetError, BrokenPipeError, ConnectionAbortedError):
            pass

    def log_message(self, format, *args):
        try:
            sys.stderr.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format % args))
            sys.stderr.flush()
        except Exception:
            pass

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

class ThreadedServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def handle_error(self, request, client_address):
        exc = sys.exc_info()[1]
        if isinstance(exc, (ConnectionResetError, BrokenPipeError, ConnectionAbortedError)):
            return
        # Ignore other transient disconnects
        pass

def run_server(port=PORT):
    if sys.stdout:
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except Exception:
            pass
    if sys.stderr:
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            pass
    with ThreadedServer(("", port), LeetCodeHandler) as httpd:
        print(f"\n[SERVER] Amazon LeetCode Explorer Server running at: http://localhost:{port}/")
        print(f"[DATA] Serving Amazon Interview Experiences from: {DATA_FILE}")
        print(f"[UI] Front-end files served from: {UI_DIR}\n")
        
        while True:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\nShutting down server...")
                httpd.server_close()
                break
            except Exception:
                pass

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    run_server(port)
