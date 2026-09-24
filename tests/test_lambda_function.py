"""
Tests for the Lambda API routes.

These tests fake DynamoDB by mocking dynamodb_store.
They do not need AWS.

Run:

    python3 -m unittest tests/test_lambda_function.py
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "lambda_src"))

import employee_rules
import lambda_function


def _http_event(
    method,
    path,
    query=None,
    body=None,
    employee_id=None,
    email="manager@example.com",
    groups="managers",
):
    claims = {"email": email}
    if groups is not None:
        claims["cognito:groups"] = groups

    event = {
        "rawPath": path,
        "requestContext": {
            "http": {"method": method},
            "authorizer": {"jwt": {"claims": claims}},
        },
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

    def test_search_rejects_long_query(self):
        long_query = "a" * 81
        with self.assertRaises(ValueError) as caught:
            employee_rules._check_search(long_query)
        self.assertEqual(str(caught.exception), "Search must be 80 characters or less.")

        with patch(
            "lambda_function.store.search_employees",
            side_effect=ValueError("Search must be 80 characters or less."),
        ):
            response = lambda_function.lambda_handler(
                _http_event("GET", "/api/employees", query={"q": long_query}),
                None,
            )
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(_body(response)["error"], "Search must be 80 characters or less.")

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

    def test_rate_publishes_sns_message(self):
        person = {
            "id": "a1",
            "name": "Ada",
            "ratings": [{"score": 5, "comment": "Good"}],
        }
        fake_boto3 = MagicMock()
        event = _http_event(
            "POST",
            "/api/employees/a1/ratings",
            employee_id="a1",
            email="manager@example.com",
            body={"score": 5, "comment": "Good"},
        )
        with patch.dict(os.environ, {"RATING_TOPIC_ARN": "arn:aws:sns:af-south-1:1:ratings"}):
            with patch("lambda_function.store.rate_employee", return_value=person):
                with patch.dict(sys.modules, {"boto3": fake_boto3}):
                    response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 200)
        fake_boto3.client.return_value.publish.assert_called_once_with(
            TopicArn="arn:aws:sns:af-south-1:1:ratings",
            Subject="New employee rating",
            Message="manager@example.com rated Ada 5/5. Good",
        )

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

    def test_add_rejects_bad_email(self):
        with self.assertRaises(ValueError) as caught:
            employee_rules._check_employee_fields(
                "Ada",
                "Engineering",
                "Developer",
                "ada-example.com",
            )
        self.assertEqual(str(caught.exception), "Email must look like name@example.com.")

        with patch(
            "lambda_function.store.add_employee",
            side_effect=ValueError("Email must look like name@example.com."),
        ):
            response = lambda_function.lambda_handler(
                _http_event(
                    "POST",
                    "/api/employees",
                    body={
                        "name": "Ada",
                        "department": "Engineering",
                        "job_title": "Developer",
                        "email": "ada-example.com",
                    },
                ),
                None,
            )
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(_body(response)["error"], "Email must look like name@example.com.")

    def test_rate_rejects_long_comment(self):
        long_comment = "x" * 201
        with self.assertRaises(ValueError) as caught:
            employee_rules._check_comment(long_comment)
        self.assertEqual(str(caught.exception), "Comment must be 200 characters or less.")

        with patch(
            "lambda_function.store.rate_employee",
            side_effect=ValueError("Comment must be 200 characters or less."),
        ):
            response = lambda_function.lambda_handler(
                _http_event(
                    "POST",
                    "/api/employees/a1/ratings",
                    employee_id="a1",
                    body={"score": 5, "comment": long_comment},
                ),
                None,
            )
        self.assertEqual(response["statusCode"], 400)
        self.assertEqual(
            _body(response)["error"],
            "Comment must be 200 characters or less.",
        )

    def test_comment_blank_becomes_no_comment(self):
        self.assertEqual(employee_rules._check_comment("   "), "(no comment)")

    def test_good_employee_fields_pass(self):
        name, department, job_title, email = employee_rules._check_employee_fields(
            "Ada Lovelace",
            "Engineering",
            "Developer",
            "ada@example.com",
        )
        self.assertEqual(name, "Ada Lovelace")
        self.assertEqual(department, "Engineering")
        self.assertEqual(job_title, "Developer")
        self.assertEqual(email, "ada@example.com")

    def test_employee_cannot_delete(self):
        event = _http_event(
            "DELETE",
            "/api/employees/a1",
            employee_id="a1",
            email="ada@example.com",
            groups=None,
        )
        with patch(
            "lambda_function.role_store.get_role",
            return_value={"email": "ada@example.com", "status": "employee"},
        ):
            with patch("lambda_function.store.delete_employee") as delete_employee:
                response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 403)
        self.assertEqual(_body(response)["error"], "You are not allowed to do that.")
        delete_employee.assert_not_called()

    def test_employee_list_returns_only_own_email(self):
        people = [
            {"id": "a1", "name": "Ada", "email": "ada@example.com"},
            {"id": "b2", "name": "Grace", "email": "grace@example.com"},
        ]
        event = _http_event(
            "GET",
            "/api/employees",
            email="ada@example.com",
            groups=None,
        )
        with patch(
            "lambda_function.role_store.get_role",
            return_value={"email": "ada@example.com", "status": "employee"},
        ):
            with patch("lambda_function.store.list_employees", return_value=people):
                response = lambda_function.lambda_handler(event, None)
        employees = _body(response)["employees"]
        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(len(employees), 1)
        self.assertEqual(employees[0]["email"], "ada@example.com")

    def test_pending_cannot_add(self):
        event = _http_event(
            "POST",
            "/api/employees",
            email="boss@example.com",
            groups=None,
            body={
                "name": "Ada",
                "department": "Engineering",
                "job_title": "Developer",
                "email": "ada@example.com",
            },
        )
        with patch(
            "lambda_function.role_store.get_role",
            return_value={"email": "boss@example.com", "status": "pending"},
        ):
            with patch("lambda_function.store.add_employee") as add_employee:
                response = lambda_function.lambda_handler(event, None)
        self.assertEqual(response["statusCode"], 403)
        add_employee.assert_not_called()

    def test_admin_approve_adds_manager_group(self):
        event = _http_event(
            "POST",
            "/api/manager-requests/approve",
            email="admin@example.com",
            groups="admins",
            body={"email": "Boss@Example.com"},
        )
        fake_boto3 = MagicMock()
        with patch(
            "lambda_function.role_store.get_role",
            return_value={"email": "boss@example.com", "status": "pending"},
        ):
            with patch("lambda_function.role_store.mark_approved") as mark_approved:
                with patch.dict(sys.modules, {"boto3": fake_boto3}):
                    response = lambda_function.lambda_handler(event, None)

        self.assertEqual(response["statusCode"], 200)
        self.assertEqual(_body(response)["ok"], True)
        mark_approved.assert_called_once_with("boss@example.com")
        fake_boto3.client.return_value.admin_add_user_to_group.assert_called_once_with(
            UserPoolId="",
            Username="boss@example.com",
            GroupName="managers",
        )


if __name__ == "__main__":
    unittest.main()
