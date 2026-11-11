"""Loopback-only HTTP fixtures; no third-party protection is reproduced."""
from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import time


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == "/content":
            status, body = 200, b"expected content: local fixture"
        elif self.path == "/captcha":
            status, body = 200, b"expected content: generic CAPTCHA exercise"
        elif self.path == "/redirect":
            status, body = 302, b"redirect fixture"
        elif self.path == "/slow":
            time.sleep(0.15)
            status, body = 200, b"expected content: slow fixture"
        elif self.path == "/cut":
            self.send_response(200)
            self.send_header("Content-Length", "100")
            self.end_headers()
            self.wfile.write(b"cut")
            self.wfile.flush()
            self.close_connection = True
            return
        else:
            status, body = 404, b"missing fixture"
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        if status == 302:
            self.send_header("Location", "/content")
        self.end_headers()
        try:
            self.wfile.write(body)
        except BrokenPipeError:
            pass

    def log_message(self, *args):
        pass


@contextmanager
def local_lab():
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
