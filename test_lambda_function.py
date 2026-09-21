"""
Tests for the Lambda API routes.

These tests fake DynamoDB by mocking dynamodb_store.
They do not need AWS.

Run:

    python3 -m unittest test_lambda_function.py
"""

import json
import os
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lambda_src"))

import lambda_function


def _http_event(method, path, query=None, body=None, employee_id=None):
    event = {
        "rawPath": path,
        "requestContext": {"http": {"method": method}},
        "queryStringParameters": query,
        "pathParameters": None,
        "body": None,
    }
    if employee_id is not None:
        event["pathParameters"] = {"id": employee_id}
    if body is not None:
        event["body"] = json.dumps(body)
    return event


def _body(response):
    return json.loads(response["body"])


class TestLambdaFunction(unittest.TestCase):
    def test_list_employees(self):
        people = [{"id": "a1", "name": "Ada"}]
        with patch("lambda_function.store.list_employees", return_value=people):
            response = lambda_function.lambda_handler(
                _http_event("GET", "/api/employees"),
                None,
            )
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(_body(response)["employees"][0]["name"], "Ada")

    def test_list_employees_with_prod_stage(self):
        people = [{"id": "a1", "name": "Ada"}]
        event = _http_event("GET", "/prod/api/employees")
        event["requestContext"]["stage"] = "prod"
        with patch("lambda_function.store.list_employees", return_value=people):
            response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(_body(response)["employees"][0]["name"], "Ada")

    def test_search_employees(self):
        people = [{"id": "a1", "name": "Ada"}]
        with patch("lambda_function.store.search_employees", return_value=people) as search:
            response = lambda_function.lambda_handler(
                _http_event("GET", "/api/employees", query={"q": "ada"}),
                None,
            )
        search.assert_called_once_with("ada")
        self.assertEqual(response["statusCode"], 200)

    def test_get_one_employee(self):
        person = {"id": "a1", "name": "Ada"}
        with patch("lambda_function.store.get_employee_by_id", return_value=person):
            response = lambda_function.lambda_handler(
                _http_event("GET", "/api/employees/a1", employee_id="a1"),
                None,
            )
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(_body(response)["employee"]["id"], "a1")

    def test_get_missing_employee(self):
        with patch("lambda_function.store.get_employee_by_id", return_value=None):
            response = lambda_function.lambda_handler(
                _http_event("GET", "/api/employees/nope", employee_id="nope"),
                None,
            )
        self.assertEqual(response["statusCode"], 404)

    def test_add_employee(self):
        person = {"id": "a1", "name": "Ada"}
        with patch("lambda_function.store.add_employee", return_value=person):
            response = lambda_function.lambda_handler(
                _http_event(
                    "POST",
                    "/api/employees",
                    body={"name": "Ada", "department": "Eng", "job_title": "Dev", "email": "a@x.com"},
                ),
                None,
            )
        self.assertEqual(response["statusCode"], 201)

    def test_add_rejects_empty_name(self):
        with patch(
            "lambda_function.store.add_employee",
            side_effect=ValueError("Name cannot be empty."),
        ):
            response = lambda_function.lambda_handler(
                _http_event("POST", "/api/employees", body={"name": ""}),
                None,
            )
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(_body(response)["error"], "Name cannot be empty.")

    def test_rate_employee(self):
        person = {"id": "a1", "ratings": [{"score": 5, "comment": "Good"}]}
        with patch("lambda_function.store.rate_employee", return_value=person):
            response = lambda_function.lambda_handler(
                _http_event(
                    "POST",
                    "/api/employees/a1/ratings",
                    employee_id="a1",
                    body={"score": 5, "comment": "Good"},
                ),
                None,
            )
        self.assertEqual(response["statusCode"], 200)

    def test_edit_employee(self):
        person = {"id": "a1", "name": "Ada L"}
        with patch("lambda_function.store.edit_employee", return_value=person):
            response = lambda_function.lambda_handler(
                _http_event(
                    "PUT",
                    "/api/employees/a1",
                    employee_id="a1",
                    body={"name": "Ada L", "department": "Math", "job_title": "Dev", "email": "a@x.com"},
                ),
                None,
            )
        self.assertEqual(response["statusCode"], 200)

    def test_delete_employee(self):
        with patch("lambda_function.store.delete_employee", return_value=True):
            response = lambda_function.lambda_handler(
                _http_event("DELETE", "/api/employees/a1", employee_id="a1"),
                None,
            )
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(_body(response)["ok"], True)


if __name__ == "__main__":
    unittest.main()
