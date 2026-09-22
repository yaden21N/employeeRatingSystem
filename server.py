"""
Local web server for the employee rating system.

The browser page talks to this server. The server uses employee_store
(the same JSON file as the terminal app).

Run:

    python3 server.py

Then open http://127.0.0.1:8000 in your browser.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

from employee_store import (
    add_employee,
    as_employee,
    as_employee_list,
    as_error,
    delete_employee,
    edit_employee,
    get_employee_by_id,
    list_employees,
    rate_employee,
    search_employees,
)

PORT = 8000
WEB_FOLDER = os.path.join(os.path.dirname(__file__), "web")

WEB_FILES = {
    "/": ("index.html", "text/html"),
    "/index.html": ("index.html", "text/html"),
    "/styles.css": ("styles.css", "text/css"),
    "/app.js": ("app.js", "text/javascript"),
    "/cognito.js": ("cognito.js", "text/javascript"),
    "/config.js": ("config.js", "text/javascript"),
}


class EmployeeHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/api/employees":
            search_text = ""
            if "q" in query:
                search_text = query["q"][0]
            if search_text == "":
                employees = list_employees()
            else:
                employees = search_employees(search_text)
            self._send_json(200, as_employee_list(employees))
            return

        if path.startswith("/api/employees/"):
            employee_id = path.replace("/api/employees/", "")
            if "/" not in employee_id and employee_id != "":
                employee = get_employee_by_id(employee_id)
                if employee is None:
                    self._send_json(404, as_error("No employee with that ID."))
                    return
                self._send_json(200, as_employee(employee))
                return

        if path in WEB_FILES:
            file_name, content_type = WEB_FILES[path]
            self._send_file(file_name, content_type)
            return

        self.send_error(404, "Not found")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/employees":
            data = self._read_json_body()
            if data is None:
                return
            try:
                employee = add_employee(
                    data.get("name"),
                    data.get("department"),
                    data.get("job_title"),
                    data.get("email"),
                )
            except ValueError as error:
                self._send_json(400, as_error(str(error)))
                return
            self._send_json(201, as_employee(employee))
            return

        if path.startswith("/api/employees/") and path.endswith("/ratings"):
            middle = path[len("/api/employees/"):]
            employee_id = middle[: -len("/ratings")]
            data = self._read_json_body()
            if data is None:
                return
            try:
                updated = rate_employee(
                    employee_id,
                    data.get("score"),
                    data.get("comment"),
                )
            except ValueError as error:
                self._send_json(400, as_error(str(error)))
                return
            if updated is None:
                self._send_json(404, as_error("No employee with that ID."))
                return
            self._send_json(200, as_employee(updated))
            return

        self.send_error(404, "Not found")

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/employees/"):
            employee_id = path.replace("/api/employees/", "")
            if "/" in employee_id or employee_id == "":
                self.send_error(404, "Not found")
                return
            data = self._read_json_body()
            if data is None:
                return
            try:
                updated = edit_employee(
                    employee_id,
                    data.get("name"),
                    data.get("department"),
                    data.get("job_title"),
                    data.get("email"),
                )
            except ValueError as error:
                self._send_json(400, as_error(str(error)))
                return
            if updated is None:
                self._send_json(404, as_error("No employee with that ID."))
                return
            self._send_json(200, as_employee(updated))
            return

        self.send_error(404, "Not found")

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/employees/"):
            employee_id = path.replace("/api/employees/", "")
            if "/" in employee_id or employee_id == "":
                self.send_error(404, "Not found")
                return
            found = delete_employee(employee_id)
            if not found:
                self._send_json(404, as_error("No employee with that ID."))
                return
            self._send_json(200, {"ok": True})
            return

        self.send_error(404, "Not found")

    def _read_json_body(self):
        length_text = self.headers.get("Content-Length", "0")
        try:
            length = int(length_text)
        except ValueError:
            length = 0

        raw = self.rfile.read(length)
        if raw == b"":
            self._send_json(400, as_error("Request body is missing."))
            return None

        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(400, as_error("Body must be JSON."))
            return None

    def _send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
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
        print("Request:", self.command, self.path)


def main():
    server = HTTPServer(("127.0.0.1", PORT), EmployeeHandler)
    print("Server running at http://127.0.0.1:" + str(PORT), flush=True)
    print("Open that address in your browser.", flush=True)
    print("Press Ctrl+C to stop.", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
