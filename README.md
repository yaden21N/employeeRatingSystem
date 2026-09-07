# Employee Rating System

Terminal app for a manager to add employees, search them, and rate them.

This is a starting version (local Python, no AWS yet). It uses the same ideas i will later put in the cloud: store data, look it up, and update it.

## How to run

You need Python 3.

```bash
python3 main.py
```

Then use the menu:

1. Add employee
2. Search employee
3. Rate employee
4. List all employees
5. Exit

Data is saved in `employees.json` in this folder.

## How to run the tests

```bash
python3 -m unittest test_employee_store.py
```

The tests use a fake file so they do not change your real employee data.

## What this version does

- Add name, department, job title, and email
- Give each employee a short ID
- Search by name, department, job title, or ID
- Rate from 1 to 5 with a comment
- Show the average score

## How this can grow into the AWS elective

The capstone is a **serverless** app (API Gateway, Lambda, DynamoDB, Cognito, S3, CloudFront, IaC). This employee app can use the same pattern later:

| Now (terminal) | Later (AWS) |
| --- | --- |
| `employees.json` | DynamoDB table |
| Python functions in `employee_store.py` | Lambda functions |
| Keyboard menu | Web app on S3 + CloudFront, or API Gateway |
| No login | Amazon Cognito (manager login) |
| One computer | Cloud, more users, notifications |


## Files

- `main.py` — menu and user input
- `employee_store.py` — load, save, search, and rate
- `test_employee_store.py` — tests for the store functions
- `employees.json` — created after you add the first employee
