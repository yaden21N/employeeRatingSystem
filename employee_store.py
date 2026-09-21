"""
Load and save employees from a JSON file.

Later this file would be replaced with DynamoDB calls.
"""

import json
import os
import uuid

DATA_FILE = "employees.json"


def load_employees():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as file:
        return json.load(file)


def save_employees(employees):
    with open(DATA_FILE, "w") as file:
        json.dump(employees, file, indent=2)


def as_employee_list(employees):
    return {"employees": employees}


def as_employee(employee):
    return {"employee": employee}


def as_error(message):
    return {"error": message}


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _check_employee_fields(name, department, job_title, email):
    name = _clean_text(name)
    department = _clean_text(department)
    job_title = _clean_text(job_title)
    email = _clean_text(email)

    if name == "":
        raise ValueError("Name cannot be empty.")

    return name, department, job_title, email


def _check_score(score):
    if isinstance(score, bool):
        raise ValueError("Score must be a number from 1 to 5.")

    if isinstance(score, str):
        if not score.isdigit():
            raise ValueError("Score must be a number from 1 to 5.")
        score = int(score)

    if isinstance(score, float):
        if score != int(score):
            raise ValueError("Score must be a number from 1 to 5.")
        score = int(score)

    if not isinstance(score, int):
        raise ValueError("Score must be a number from 1 to 5.")

    if score < 1 or score > 5:
        raise ValueError("Score must be from 1 to 5.")

    return score


def add_employee(name, department, job_title, email):
    name, department, job_title, email = _check_employee_fields(
        name, department, job_title, email
    )

    employees = load_employees()
    employee = {
        "id": str(uuid.uuid4())[:8],
        "name": name,
        "department": department,
        "job_title": job_title,
        "email": email,
        "ratings": [],
    }
    employees.append(employee)
    save_employees(employees)
    return employee


def list_employees():
    employees = load_employees()
    employees.sort(key=lambda employee: employee["name"].lower())
    return employees


def get_employee_by_id(employee_id):
    employees = load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None


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

    employees = load_employees()
    updated = None

    for employee in employees:
        if employee["id"] == employee_id:
            employee["ratings"].append({
                "score": score,
                "comment": comment,
            })
            updated = employee
            break

    if updated is not None:
        save_employees(employees)

    return updated


def edit_employee(employee_id, name, department, job_title, email):
    name, department, job_title, email = _check_employee_fields(
        name, department, job_title, email
    )

    employees = load_employees()
    updated = None

    for employee in employees:
        if employee["id"] == employee_id:
            employee["name"] = name
            employee["department"] = department
            employee["job_title"] = job_title
            employee["email"] = email
            updated = employee
            break

    if updated is not None:
        save_employees(employees)

    return updated


def delete_employee(employee_id):
    employees = load_employees()
    kept = []
    found = False

    for employee in employees:
        if employee["id"] == employee_id:
            found = True
        else:
            kept.append(employee)

    if found:
        save_employees(kept)

    return found
