"""Lokaler Static-Server fuer die Pruefskripte (Thread, freier Port, Repo-Root, no-store)."""
import functools, http.server, socketserver, threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def start():
    handler = functools.partial(_Quiet, directory=str(ROOT))
    srv = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"
