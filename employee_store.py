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


def add_employee(name, department, job_title, email):
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
    return load_employees()


def get_employee_by_id(employee_id):
    employees = load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            return employee
    return None


def search_employees(query):
    query = query.lower()
    employees = load_employees()
    results = []

    for employee in employees:
        name = employee["name"].lower()
        department = employee["department"].lower()
        employee_id = employee["id"].lower()
        job_title = employee["job_title"].lower()

        if query in name or query in department or query in employee_id or query in job_title:
            results.append(employee)

    return results


def rate_employee(employee_id, score, comment):
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
