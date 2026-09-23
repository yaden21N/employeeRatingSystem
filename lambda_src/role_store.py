"""
Who asked to be a manager, and who chose to be an employee.

One row per email. status is employee, pending, or approved.
"""

import os


def _table():
    import boto3

    table_name = os.environ.get("ROLE_TABLE_NAME", "Roles")
    return boto3.resource("dynamodb").Table(table_name)


def _clean_email(email):
    if email is None:
        return ""
    return str(email).strip().lower()


def get_role(email):
    email = _clean_email(email)
    response = _table().get_item(Key={"email": email})
    item = response.get("Item")
    if item is None:
        return None
    return {"email": item["email"], "status": item["status"]}


def save_choice(email, choice):
    email = _clean_email(email)
    if choice != "employee" and choice != "manager":
        raise ValueError("Choice must be employee or manager.")

    existing = get_role(email)
    if existing is not None:
        raise ValueError("You already chose a role.")

    if choice == "employee":
        status = "employee"
    else:
        status = "pending"

    _table().put_item(Item={"email": email, "status": status})
    return {"email": email, "status": status}


def list_pending():
    table = _table()
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    pending = []
    for item in items:
        if item.get("status") == "pending":
            pending.append({"email": item["email"], "status": "pending"})

    pending.sort(key=lambda row: row["email"])
    return pending


def mark_approved(email):
    email = _clean_email(email)
    _table().put_item(Item={"email": email, "status": "approved"})


def add_user_to_managers(email):
    import boto3

    email = _clean_email(email)
    user_pool_id = os.environ.get("USER_POOL_ID", "")
    client = boto3.client("cognito-idp")
    client.admin_add_user_to_group(
        UserPoolId=user_pool_id,
        Username=email,
        GroupName="managers",
    )
