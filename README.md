# Employee Rating System

Hosted web app for rating employees. An admin approves managers. A manager can add, search, rate, edit, and delete employees. An employee can see only their own ratings.

Open the site: [https://d256npmkht54jg.cloudfront.net](https://d256npmkht54jg.cloudfront.net)



## How to run the tests

```bash
python3 -m unittest tests/test_lambda_function.py
```

The Lambda tests fake DynamoDB and Cognito, so they do not need AWS.

## What this version does

- Add name, department, job title, and email
- Give each employee a short ID
- Search by name, department, job title, email, or ID
- Rate from 1 to 5 with a comment
- Show the average score
- Edit details
- Delete an employee
- Reject an empty name, a bad email, a score that is not 1 to 5, and text that is too long
- Three roles: admin, manager, and employee



## API

The CloudFront page calls this API. API Gateway requires a Cognito id token.


| Method | Path                            | What it does                           |
| ------ | ------------------------------- | -------------------------------------- |
| GET    | `/api/role`                     | Who is logged in                       |
| POST   | `/api/role`                     | Choose employee or ask to be a manager |
| GET    | `/api/manager-requests`         | Pending manager requests (admin)       |
| POST   | `/api/manager-requests/approve` | Approve a manager (admin)              |
| GET    | `/api/employees`                | List (sorted by name)                  |
| GET    | `/api/employees?q=ada`          | Search                                 |
| GET    | `/api/employees/{id}`           | One employee                           |
| POST   | `/api/employees`                | Add                                    |
| PUT    | `/api/employees/{id}`           | Edit                                   |
| DELETE | `/api/employees/{id}`           | Delete                                 |
| POST   | `/api/employees/{id}/ratings`   | Rate                                   |


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



## How to deploy

You need the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) and an AWS account.

```bash
sam build
sam deploy
python3 upload_web.py
```

`upload_web.py` copies `web/` to the S3 bucket, writes the API URL and Cognito client id into `config.js` for that upload, then restores the empty local `config.js`. SAM prints `WebsiteUrl`.

The browser is on CloudFront. The API is on API Gateway. That is a different website, so the API allows CORS (`Access-Control-Allow-Origin: *` on Lambda, plus CORS on the HTTP API).

## Rating notices

After a rating is saved, Lambda publishes a message to an SNS topic named `employee-rating-ratings`. To get those messages by email, deploy with your address:

```bash
sam deploy --parameter-overrides NotifyEmail=you@example.com
```

AWS emails that address a confirmation link. Notices start after you confirm it.

## Cybersecurity

This section is the capstone write-up. Later security work stays here too.

### Login

The password goes to Cognito. The API sees an id token, not the password.

1. The page sends the email and password to Cognito (`web/cognito.js`).
2. Cognito returns an id token. The page stores it in `sessionStorage`.
3. Each API call sends `Authorization: Bearer` plus that token (`web/app.js`).
4. API Gateway checks the token before Lambda runs (`template.yaml`).
5. Lambda reads the email and Cognito groups from the token (`_caller` in `lambda_src/lambda_function.py`).

A call with no email on the token gets status 401.

### Roles

`_access_role` in `lambda_src/lambda_function.py` picks the role. Admin and manager come from Cognito groups. The other roles come from the Roles table.

- **none** — no group and no row yet. The user must choose employee or ask to be a manager. Employee routes return 403.
- **pending** — asked to be a manager and is waiting for an admin. Employee routes return 403.
- **approved** — an admin approved the request and added the user to the managers group. The user logs out and logs in again so the new token includes that group.
- **employee** — can list and open only the row with their own email. Add, edit, delete, and rate return 403.
- **manager** — can list, search, add, edit, delete, and rate every employee.
- **admin** — can do what a manager can do, and can list and approve manager requests.

The page shows or hides the matching screen. Lambda is the check that allows or blocks the action.

### Role tests

`python3 -m unittest tests/test_lambda_function.py` runs 19 tests. These four check roles:

- `test_employee_list_returns_only_own_email` — an employee list contains only that employee's row
- `test_employee_cannot_delete` — an employee delete returns 403
- `test_pending_cannot_add` — a pending user cannot add an employee
- `test_admin_approve_adds_manager_group` — an admin approve adds the user to the managers group

## Files

- `web/index.html` — web page
- `web/styles.css` — page styles
- `web/app.js` — talks to the API and updates the page
- `web/cognito.js` — sign up, confirm, and log in
- `web/config.js` — API URL and Cognito ids (empty in git; filled only during upload)
- `upload_web.py` — copies `web/` to S3 and refreshes CloudFront
- `tests/test_lambda_function.py` — tests for the Lambda routes
- `template.yaml` — SAM template (tables, Lambda, API Gateway, S3, CloudFront, Cognito, SNS)
- `lambda_src/` — Lambda code that reads and writes DynamoDB

