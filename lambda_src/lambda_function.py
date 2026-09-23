"""
Lambda handler for the employee API.

Paths match server.py so the web page can use the same URLs later.
"""

import json

import dynamodb_store as store
import role_store
from employee_rules import as_employee, as_employee_list, as_error

NOT_ALLOWED = "You are not allowed to do that."


def lambda_handler(event, context):
    method = _http_method(event)
    path = _http_path(event)
    query = event.get("queryStringParameters") or {}
    path_id = _path_id(event)
    caller = _caller(event)

    if caller["email"] == "":
        return _json(401, as_error("Please log in again."))

    if method == "GET" and path == "/api/role":
        return _json(200, {"email": caller["email"], "role": _access_role(caller)})

    if method == "POST" and path == "/api/role":
        return _choose_role(caller, event)

    if method == "GET" and path == "/api/manager-requests":
        return _list_manager_requests(caller)

    if method == "POST" and path == "/api/manager-requests/approve":
        return _approve_manager(caller, event)

    role = _access_role(caller)
    if role != "admin" and role != "manager" and role != "employee":
        return _json(403, as_error(NOT_ALLOWED))

    if method == "GET" and path == "/api/employees":
        search_text = query.get("q") or ""
        if search_text == "":
            employees = store.list_employees()
        else:
            employees = store.search_employees(search_text)
        employees = _only_own_rows(role, caller["email"], employees)
        return _json(200, as_employee_list(employees))

    if method == "GET" and path_id is not None and not path.endswith("/ratings"):
        employee = store.get_employee_by_id(path_id)
        if employee is None:
            return _json(404, as_error("No employee with that ID."))
        if not _can_see_employee(role, caller["email"], employee):
            return _json(403, as_error(NOT_ALLOWED))
        return _json(200, as_employee(employee))

    if role == "employee":
        return _json(403, as_error(NOT_ALLOWED))

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


def _caller(event):
    request_context = event.get("requestContext") or {}
    authorizer = request_context.get("authorizer") or {}
    jwt = authorizer.get("jwt") or {}
    claims = jwt.get("claims") or {}
    email = claims.get("email") or ""
    email = str(email).strip().lower()
    groups = _group_names(claims.get("cognito:groups"))
    return {"email": email, "groups": groups}


def _group_names(groups):
    if groups is None:
        return []

    if isinstance(groups, list):
        names = groups
    else:
        text = str(groups).strip()
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        names = text.split(",")

    clean = []
    for name in names:
        name = str(name).strip()
        if name != "":
            clean.append(name)
    return clean


def _access_role(caller):
    if "admins" in caller["groups"]:
        return "admin"
    if "managers" in caller["groups"]:
        return "manager"

    row = role_store.get_role(caller["email"])
    if row is None:
        return "none"
    if row["status"] == "employee":
        return "employee"
    if row["status"] == "pending":
        return "pending"
    if row["status"] == "approved":
        return "approved"
    return "none"


def _choose_role(caller, event):
    if "admins" in caller["groups"] or "managers" in caller["groups"]:
        return _json(400, as_error("You already have a role."))

    data = _read_body(event)
    if data is None:
        return _json(400, as_error("Body must be JSON."))

    try:
        saved = role_store.save_choice(caller["email"], data.get("choice"))
    except ValueError as error:
        return _json(400, as_error(str(error)))

    if saved["status"] == "pending":
        role = "pending"
    else:
        role = "employee"
    return _json(200, {"email": saved["email"], "role": role})


def _list_manager_requests(caller):
    if _access_role(caller) != "admin":
        return _json(403, as_error(NOT_ALLOWED))
    return _json(200, {"requests": role_store.list_pending()})


def _approve_manager(caller, event):
    if _access_role(caller) != "admin":
        return _json(403, as_error(NOT_ALLOWED))

    data = _read_body(event)
    if data is None:
        return _json(400, as_error("Body must be JSON."))

    email = str(data.get("email") or "").strip().lower()
    if email == "":
        return _json(400, as_error("Email cannot be empty."))

    row = role_store.get_role(email)
    if row is None:
        return _json(404, as_error("No request with that email."))
    if row["status"] != "pending":
        return _json(400, as_error("That person is not waiting for approval."))

    role_store.mark_approved(email)
    role_store.add_user_to_managers(email)
    return _json(200, {"ok": True})


def _only_own_rows(role, email, employees):
    if role != "employee":
        return employees

    own = []
    for employee in employees:
        if _same_email(employee.get("email"), email):
            own.append(employee)
    return own


def _can_see_employee(role, email, employee):
    if role != "employee":
        return True
    return _same_email(employee.get("email"), email)


def _same_email(left, right):
    return str(left or "").strip().lower() == str(right or "").strip().lower()


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
