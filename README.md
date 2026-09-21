# Employee Rating System

Terminal and local web app for a manager to add employees, search them, rate them, edit them, and delete them.

This is the local version (no AWS yet). It uses the same ideas that can later go in the cloud: store data, look it up, and update it.

## How to run the web app

You need Python 3.

```bash
python3 server.py
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

On that page you can:

- search employees
- add an employee
- rate an employee (1 to 5 plus a comment)
- edit an employee
- delete an employee

## How to run the terminal app

```bash
python3 main.py
```

Menu:

1. Add employee
2. Search employee
3. Rate employee
4. List all employees
5. Edit employee
6. Delete employee
7. Exit

The web app and the terminal app share the same file: `employees.json`.

## How to run the tests

```bash
python3 -m unittest test_employee_store.py
```

The tests use a fake file so they do not change your real employee data.

## What this version does

- Add name, department, job title, and email
- Give each employee a short ID
- Search by name, department, job title, email, or ID
- Rate from 1 to 5 with a comment
- Show the average score
- Edit details
- Delete an employee
- Reject an empty name and a score that is not 1 to 5



## Local API (used by the web page)

The server is the same shape a Lambda API can use later.


| Method | Path                          | What it does              |
| ------ | ----------------------------- | ------------------------- |
| GET    | `/api/employees`              | List all (sorted by name) |
| GET    | `/api/employees?q=ada`        | Search                    |
| GET    | `/api/employees/{id}`         | One employee              |
| POST   | `/api/employees`              | Add                       |
| PUT    | `/api/employees/{id}`         | Edit                      |
| DELETE | `/api/employees/{id}`         | Delete                    |
| POST   | `/api/employees/{id}/ratings` | Rate                      |


JSON list shape:

```json
{ "employees": [] }
```

JSON one-employee shape:

```json
{ "employee": { "id": "...", "name": "..." } }
```

JSON error shape:

```json
{ "error": "Name cannot be empty." }
```



## How this can grow into the AWS :




| Now (local)                             | Later (AWS)                    |
| --------------------------------------- | ------------------------------ |
| `employees.json`                        | DynamoDB table                 |
| Python functions in `employee_store.py` | Lambda functions               |
| `server.py` on your laptop              | API Gateway                    |
| `web/` folder                           | S3 + CloudFront                |
| No login                                | Amazon Cognito (manager login) |




## Files

- `main.py` — terminal menu and user input
- `employee_store.py` — load, save, search, rate, edit, delete
- `server.py` — local web server and API
- `web/index.html` — web page
- `web/styles.css` — page styles
- `web/app.js` — talks to the API and updates the page
- `test_employee_store.py` — tests for the store functions
- `employees.json` — created after you add the first employee

