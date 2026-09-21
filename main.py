"""
Employee Rating System - terminal app

A manager can:
- add employees
- search for an employee
- rate an employee
- list all employees
- edit an employee
- delete an employee

Data is saved in employees.json so it is not lost when you close the program.
"""

from employee_store import (
    add_employee,
    delete_employee,
    edit_employee,
    search_employees,
    rate_employee,
    list_employees,
    get_employee_by_id,
)


def print_menu():
    print()
    print("===== Employee Rating System =====")
    print("1. Add employee")
    print("2. Search employee")
    print("3. Rate employee")
    print("4. List all employees")
    print("5. Edit employee")
    print("6. Delete employee")
    print("7. Exit")
    print()


def show_employee(employee):
    print("--------------------------------")
    print("ID:         " + employee["id"])
    print("Name:       " + employee["name"])
    print("Department: " + employee["department"])
    print("Job title:  " + employee["job_title"])
    print("Email:      " + employee["email"])
    ratings = employee["ratings"]
    if len(ratings) == 0:
        print("Ratings:    none yet")
    else:
        total = 0
        for rating in ratings:
            total = total + rating["score"]
        average = total / len(ratings)
        print("Ratings:    " + str(len(ratings)) + " review(s), average " + str(round(average, 1)) + "/5")
        for rating in ratings:
            print("  - " + str(rating["score"]) + "/5 : " + rating["comment"])
    print("--------------------------------")


def handle_add_employee():
    print()
    print("--- Add employee ---")
    name = input("Full name: ").strip()
    department = input("Department: ").strip()
    job_title = input("Job title: ").strip()
    email = input("Email: ").strip()

    try:
        employee = add_employee(name, department, job_title, email)
    except ValueError as error:
        print(str(error))
        return

    print("Employee added.")
    show_employee(employee)


def handle_search_employee():
    print()
    print("--- Search employee ---")
    query = input("Type a name, department, job title, email, or ID: ").strip()
    results = search_employees(query)

    if len(results) == 0:
        print("No employees found.")
        return

    print("Found " + str(len(results)) + " employee(s):")
    for employee in results:
        show_employee(employee)


def handle_rate_employee():
    print()
    print("--- Rate employee ---")
    employee_id = input("Employee ID: ").strip()
    employee = get_employee_by_id(employee_id)

    if employee is None:
        print("No employee with that ID. Use search or list to find the ID.")
        return

    show_employee(employee)

    score_text = input("Score (1 to 5): ").strip()
    comment = input("Comment: ").strip()

    try:
        updated = rate_employee(employee_id, score_text, comment)
    except ValueError as error:
        print(str(error))
        return

    print("Rating saved.")
    show_employee(updated)


def handle_list_employees():
    print()
    print("--- All employees ---")
    employees = list_employees()
    if len(employees) == 0:
        print("No employees yet. Add one from the menu.")
        return

    for employee in employees:
        show_employee(employee)


def handle_edit_employee():
    print()
    print("--- Edit employee ---")
    employee_id = input("Employee ID: ").strip()
    employee = get_employee_by_id(employee_id)

    if employee is None:
        print("No employee with that ID. Use search or list to find the ID.")
        return

    show_employee(employee)
    print("Leave a field blank to keep the old value.")
    name = input("Full name [" + employee["name"] + "]: ").strip()
    department = input("Department [" + employee["department"] + "]: ").strip()
    job_title = input("Job title [" + employee["job_title"] + "]: ").strip()
    email = input("Email [" + employee["email"] + "]: ").strip()

    if name == "":
        name = employee["name"]
    if department == "":
        department = employee["department"]
    if job_title == "":
        job_title = employee["job_title"]
    if email == "":
        email = employee["email"]

    try:
        updated = edit_employee(employee_id, name, department, job_title, email)
    except ValueError as error:
        print(str(error))
        return

    print("Employee updated.")
    show_employee(updated)


def handle_delete_employee():
    print()
    print("--- Delete employee ---")
    employee_id = input("Employee ID: ").strip()
    employee = get_employee_by_id(employee_id)

    if employee is None:
        print("No employee with that ID. Use search or list to find the ID.")
        return

    show_employee(employee)
    confirm = input("Type yes to delete this employee: ").strip().lower()
    if confirm != "yes":
        print("Delete cancelled.")
        return

    delete_employee(employee_id)
    print("Employee deleted.")


def main():
    print("Welcome. Employee data is stored in employees.json.")
    print("You can also use the web app: python3 server.py")

    while True:
        print_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "1":
            handle_add_employee()
        elif choice == "2":
            handle_search_employee()
        elif choice == "3":
            handle_rate_employee()
        elif choice == "4":
            handle_list_employees()
        elif choice == "5":
            handle_edit_employee()
        elif choice == "6":
            handle_delete_employee()
        elif choice == "7":
            print("Goodbye.")
            break
        else:
            print("Please type a number from 1 to 7.")


if __name__ == "__main__":
    main()
