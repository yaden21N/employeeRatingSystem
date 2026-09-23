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

## How Cognito login works

The HTTP API requires a Cognito id token. The page sends `Authorization: Bearer ...` on every API call. Passwords stay in Cognito.

After you change the template or the web files, deploy again and re-upload the site:

```bash
sam build
sam deploy
python3 upload_web.py
```



## Files

- `web/index.html` — web page
- `web/styles.css` — page styles
- `web/app.js` — talks to the API and updates the page
- `web/cognito.js` — sign up, confirm, and log in
- `web/config.js` — API URL and Cognito ids (empty in git; filled only during upload)
- `upload_web.py` — copies `web/` to S3 and refreshes CloudFront
- `tests/test_lambda_function.py` — tests for the Lambda routes
- `template.yaml` — SAM template (tables, Lambda, API Gateway, S3, CloudFront, Cognito)
- `lambda_src/` — Lambda code that reads and writes DynamoDB

