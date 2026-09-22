# Employee Rating System

Terminal and local web app for a manager to add employees, search them, rate them, edit them, and delete them.

This is the local version plus an AWS API (DynamoDB, Lambda, API Gateway) and a cloud web page (S3 + CloudFront). The laptop app still uses `employees.json`. The cloud app uses a DynamoDB table.

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
python3 -m unittest test_employee_store.py test_lambda_function.py
```

The store tests use a fake file so they do not change your real employee data.
The Lambda tests fake DynamoDB so they do not need AWS.

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



## How to deploy the AWS API

You need the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) and an AWS account.

```bash
sam build
sam deploy --guided
```

After deploy, SAM prints `ApiUrl`. The paths are the same as the local server, for example:

```text
GET  {ApiUrl}/api/employees
POST {ApiUrl}/api/employees
POST {ApiUrl}/api/employees/{id}/ratings
```

The laptop web page (`python3 server.py`) still talks to the local server.

## How to put the web page on S3 and CloudFront

After the stack exists (first `sam deploy` can take several minutes because CloudFront is slow):

```bash
sam build
sam deploy
python3 upload_web.py
```

`upload_web.py` copies `web/` to the S3 bucket, writes the API URL into `config.js` for that upload, then restores the empty local `config.js`. SAM prints `WebsiteUrl`. Open that HTTPS CloudFront address.

The browser is on CloudFront. The API is on API Gateway. That is a different website, so the API allows CORS (`Access-Control-Allow-Origin: *` on Lambda, plus CORS on the HTTP API and the S3 bucket).

Cognito login is not set up yet. Anyone with the CloudFront URL can use the API.

## How this maps to AWS

| Now (local)                             | AWS now                        | Still later                    |
| --------------------------------------- | ------------------------------ | ------------------------------ |
| `employees.json`                        | DynamoDB table                 |                                |
| Python functions in `employee_store.py` | Lambda + `dynamodb_store.py`   |                                |
| `server.py` on your laptop              | API Gateway                    |                                |
| `web/` folder                           | S3 + CloudFront                |                                |
| No login                                |                                | Amazon Cognito (manager login) |




## Files

- `main.py` — terminal menu and user input
- `employee_store.py` — load, save, search, rate, edit, delete
- `server.py` — local web server and API
- `web/index.html` — web page
- `web/styles.css` — page styles
- `web/app.js` — talks to the API and updates the page
- `web/config.js` — API base URL (empty on the laptop)
- `upload_web.py` — copies `web/` to S3 and refreshes CloudFront
- `test_employee_store.py` — tests for the store functions
- `test_lambda_function.py` — tests for the Lambda routes
- `template.yaml` — SAM template (table, Lambda, API Gateway, S3, CloudFront)
- `lambda_src/` — Lambda code that reads and writes DynamoDB
- `employees.json` — created after you add the first employee (local only)

