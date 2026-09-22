"""
Shared checks and JSON shapes for the local store and the Lambda API.
"""


def _clean_text(value):
    if value is None:
        return ""
    return str(value).strip()


def _check_length(value, limit, label):
    if len(value) > limit:
        raise ValueError(label + " must be " + str(limit) + " characters or less.")


def _check_email(email):
    if email == "":
        raise ValueError("Email cannot be empty.")

    _check_length(email, 80, "Email")

    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise ValueError("Email must look like name@example.com.")

    parts = email.split("@")
    if len(parts) != 2 or "." not in parts[1] or parts[1].startswith("."):
        raise ValueError("Email must look like name@example.com.")


def _check_employee_fields(name, department, job_title, email):
    name = _clean_text(name)
    department = _clean_text(department)
    job_title = _clean_text(job_title)
    email = _clean_text(email)

    if name == "":
        raise ValueError("Name cannot be empty.")

    _check_length(name, 80, "Name")
    _check_length(department, 40, "Department")
    _check_length(job_title, 40, "Job title")
    _check_email(email)

    return name, department, job_title, email


def _check_comment(comment):
    comment = _clean_text(comment)
    _check_length(comment, 200, "Comment")
    if comment == "":
        return "(no comment)"
    return comment


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
