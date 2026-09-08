"""
Tiny local web server for Day 5.

Opens a page in the browser that lists employees.
The page asks this server for data. The server uses employee_store
(the same JSON file as the terminal app).

Run:

    python3 server.py

Then open http://127.0.0.1:8000 in your browser.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from employee_store import list_employees

PORT = 8000
WEB_FOLDER = os.path.join(os.path.dirname(__file__), "web")

# Only these files can be opened from the browser.
WEB_FILES = {
    "/": ("index.html", "text/html"),
    "/index.html": ("index.html", "text/html"),
    "/styles.css": ("styles.css", "text/css"),
    "/list.js": ("list.js", "text/javascript"),
}


class EmployeeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/employees":
            employees = list_employees()
            self._send_json(employees)
            return

        if self.path in WEB_FILES:
            file_name, content_type = WEB_FILES[self.path]
            self._send_file(file_name, content_type)
            return

        self.send_error(404, "Not found")

    def _send_json(self, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, file_name, content_type):
        file_path = os.path.join(WEB_FOLDER, file_name)
        with open(file_path, "rb") as file:
            body = file.read()

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        print("Request:", self.path)


def main():
    server = HTTPServer(("127.0.0.1", PORT), EmployeeHandler)
    print("Server running at http://127.0.0.1:" + str(PORT), flush=True)
    print("Open that address in your browser.", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
