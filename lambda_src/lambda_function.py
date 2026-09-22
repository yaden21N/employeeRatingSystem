"""
Lambda handler for the employee API.

Paths match server.py so the web page can use the same URLs later.
"""

import json

import dynamodb_store as store
from employee_rules import as_employee, as_employee_list, as_error


def lambda_handler(event, context):
    method = _http_method(event)
    path = _http_path(event)
    query = event.get("queryStringParameters") or {}
    path_id = _path_id(event)

    if method == "GET" and path == "/api/employees":
        search_text = query.get("q") or ""
        if search_text == "":
            employees = store.list_employees()
        else:
            employees = store.search_employees(search_text)
        return _json(200, as_employee_list(employees))

    if method == "GET" and path_id is not None and not path.endswith("/ratings"):
        employee = store.get_employee_by_id(path_id)
        if employee is None:
            return _json(404, as_error("No employee with that ID."))
        return _json(200, as_employee(employee))

    if method == "POST" and path == "/api/employees":
        data = _read_body(event)
        if data is None:
            return _json(400, as_error("Body must be JSON."))
        try:
            employee = store.add_employee(
                data.get("name"),
                data.get("department"),
                data.get("job_title"),
                data.get("email"),
            )
        except ValueError as error:
            return _json(400, as_error(str(error)))
        return _json(201, as_employee(employee))

    if method == "POST" and path.endswith("/ratings") and path_id is not None:
        data = _read_body(event)
        if data is None:
            return _json(400, as_error("Body must be JSON."))
        try:
            updated = store.rate_employee(
                path_id,
                data.get("score"),
                data.get("comment"),
            )
        except ValueError as error:
            return _json(400, as_error(str(error)))
        if updated is None:
            return _json(404, as_error("No employee with that ID."))
        return _json(200, as_employee(updated))

    if method == "PUT" and path_id is not None:
        data = _read_body(event)
        if data is None:
            return _json(400, as_error("Body must be JSON."))
        try:
            updated = store.edit_employee(
                path_id,
                data.get("name"),
                data.get("department"),
                data.get("job_title"),
                data.get("email"),
            )
        except ValueError as error:
            return _json(400, as_error(str(error)))
        if updated is None:
            return _json(404, as_error("No employee with that ID."))
        return _json(200, as_employee(updated))

    if method == "DELETE" and path_id is not None:
        found = store.delete_employee(path_id)
        if not found:
            return _json(404, as_error("No employee with that ID."))
        return _json(200, {"ok": True})

    return _json(404, as_error("Not found"))


def _http_method(event):
    request_context = event.get("requestContext") or {}
    http = request_context.get("http") or {}
    if "method" in http:
        return http["method"]
    return event.get("httpMethod", "GET")


def _http_path(event):
    if "rawPath" in event:
        path = event["rawPath"]
    else:
        path = event.get("path", "")

    # HTTP API adds the stage to the path, for example /prod/api/employees
    request_context = event.get("requestContext") or {}
    stage = request_context.get("stage")
    if stage and stage != "$default":
        prefix = "/" + stage
        if path == prefix or path.startswith(prefix + "/"):
            path = path[len(prefix) :]
            if path == "":
                path = "/"
    return path


def _path_id(event):
    params = event.get("pathParameters") or {}
    return params.get("id")


def _read_body(event):
    body = event.get("body")
    if body is None or body == "":
        return None
    if event.get("isBase64Encoded"):
        import base64

        body = base64.b64decode(body).decode("utf-8")
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return None


def _json(status, data):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(data),
    }
