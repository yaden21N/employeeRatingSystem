"""
Shared checks and JSON shapes for the local store and the Lambda API.
"""


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


def as_employee_list(employees):
    return {"employees": employees}


def as_employee(employee):
    return {"employee": employee}


def as_error(message):
    return {"error": message}
