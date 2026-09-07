"""
Tests for employee_store.py

These tests use a fake file (test_employees.json) so they do not
change your real employees.json.

Run them with:

    python3 -m unittest test_employee_store.py
"""

import os
import unittest

import employee_store


class TestEmployeeStore(unittest.TestCase):
    def setUp(self):
        # Runs before every test. Point the store at a test file.
        self.test_file = "test_employees.json"
        employee_store.DATA_FILE = self.test_file
        self._delete_test_file()

    def tearDown(self):
        # Runs after every test. Clean up the test file.
        self._delete_test_file()

    def _delete_test_file(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_load_employees_when_file_is_missing(self):
        employees = employee_store.load_employees()
        self.assertEqual(employees, [])

    def test_add_employee_saves_details(self):
        employee = employee_store.add_employee(
            "Ada Lovelace",
            "Engineering",
            "Developer",
            "ada@example.com",
        )

        self.assertEqual(employee["name"], "Ada Lovelace")
        self.assertEqual(employee["department"], "Engineering")
        self.assertEqual(employee["job_title"], "Developer")
        self.assertEqual(employee["email"], "ada@example.com")
        self.assertEqual(employee["ratings"], [])
        self.assertTrue(len(employee["id"]) > 0)

    def test_list_employees_returns_added_people(self):
        employee_store.add_employee("Ada Lovelace", "Engineering", "Developer", "ada@example.com")
        employee_store.add_employee("Alan Turing", "Research", "Analyst", "alan@example.com")

        employees = employee_store.list_employees()
        self.assertEqual(len(employees), 2)

    def test_get_employee_by_id_finds_person(self):
        employee = employee_store.add_employee(
            "Ada Lovelace",
            "Engineering",
            "Developer",
            "ada@example.com",
        )

        found = employee_store.get_employee_by_id(employee["id"])
        self.assertIsNotNone(found)
        self.assertEqual(found["name"], "Ada Lovelace")

    def test_get_employee_by_id_returns_none_when_missing(self):
        found = employee_store.get_employee_by_id("not-real")
        self.assertIsNone(found)

    def test_search_by_name_is_not_case_sensitive(self):
        employee_store.add_employee("Ada Lovelace", "Engineering", "Developer", "ada@example.com")

        results = employee_store.search_employees("ada")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Ada Lovelace")

    def test_search_by_department(self):
        employee_store.add_employee("Ada Lovelace", "Engineering", "Developer", "ada@example.com")
        employee_store.add_employee("Alan Turing", "Research", "Analyst", "alan@example.com")

        results = employee_store.search_employees("research")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Alan Turing")

    def test_search_returns_empty_list_when_no_match(self):
        employee_store.add_employee("Ada Lovelace", "Engineering", "Developer", "ada@example.com")

        results = employee_store.search_employees("marketing")
        self.assertEqual(results, [])

    def test_rate_employee_adds_a_rating(self):
        employee = employee_store.add_employee(
            "Ada Lovelace",
            "Engineering",
            "Developer",
            "ada@example.com",
        )

        updated = employee_store.rate_employee(employee["id"], 5, "Great work")

        self.assertEqual(len(updated["ratings"]), 1)
        self.assertEqual(updated["ratings"][0]["score"], 5)
        self.assertEqual(updated["ratings"][0]["comment"], "Great work")

    def test_rate_employee_can_add_more_than_one_rating(self):
        employee = employee_store.add_employee(
            "Ada Lovelace",
            "Engineering",
            "Developer",
            "ada@example.com",
        )

        employee_store.rate_employee(employee["id"], 4, "Good")
        updated = employee_store.rate_employee(employee["id"], 5, "Excellent")

        self.assertEqual(len(updated["ratings"]), 2)

    def test_rate_employee_returns_none_when_id_is_wrong(self):
        result = employee_store.rate_employee("not-real", 5, "Nice")
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
