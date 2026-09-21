"""
Employee data in DynamoDB.

This is the cloud version of employee_store.py (which uses a JSON file).
"""

import os
import uuid

from employee_rules import _check_employee_fields, _check_score, _clean_text


def _table():
    import boto3

    table_name = os.environ.get("TABLE_NAME", "Employees")
    return boto3.resource("dynamodb").Table(table_name)


def _from_item(item):
    ratings = []
    for rating in item.get("ratings", []):
        ratings.append({
            "score": int(rating["score"]),
            "comment": rating["comment"],
        })

    return {
        "id": item["id"],
        "name": item["name"],
        "department": item["department"],
        "job_title": item["job_title"],
        "email": item["email"],
        "ratings": ratings,
    }


def add_employee(name, department, job_title, email):
    name, department, job_title, email = _check_employee_fields(
        name, department, job_title, email
    )

    employee = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "department": department,
        "job_title": job_title,
        "email": email,
        "ratings": [],
    }
    _table().put_item(Item=employee)
    return employee


def list_employees():
    table = _table()
    items = []
    response = table.scan()
    items.extend(response.get("Items", []))

    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))

    employees = []
    for item in items:
        employees.append(_from_item(item))

    employees.sort(key=lambda employee: employee["name"].lower())
    return employees


def get_employee_by_id(employee_id):
    response = _table().get_item(Key={"id": employee_id})
    item = response.get("Item")
    if item is None:
        return None
    return _from_item(item)


def search_employees(query):
    query = _clean_text(query).lower()
    employees = list_employees()

    if query == "":
        return employees

    results = []
    for employee in employees:
        name = employee["name"].lower()
        department = employee["department"].lower()
        employee_id = employee["id"].lower()
        job_title = employee["job_title"].lower()
        email = employee["email"].lower()

        if (
            query in name
            or query in department
            or query in employee_id
            or query in job_title
            or query in email
        ):
            results.append(employee)

    return results


def rate_employee(employee_id, score, comment):
    score = _check_score(score)
    comment = _clean_text(comment)
    if comment == "":
        comment = "(no comment)"

    employee = get_employee_by_id(employee_id)
    if employee is None:
        return None

    employee["ratings"].append({
        "score": score,
        "comment": comment,
    })
    _table().put_item(Item=employee)
    return employee


def edit_employee(employee_id, name, department, job_title, email):
    name, department, job_title, email = _check_employee_fields(
        name, department, job_title, email
    )

    employee = get_employee_by_id(employee_id)
    if employee is None:
        return None

    employee["name"] = name
    employee["department"] = department
    employee["job_title"] = job_title
    employee["email"] = email
    _table().put_item(Item=employee)
    return employee


def delete_employee(employee_id):
    employee = get_employee_by_id(employee_id)
    if employee is None:
        return False

    _table().delete_item(Key={"id": employee_id})
    return True
