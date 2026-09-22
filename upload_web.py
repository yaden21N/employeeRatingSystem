"""
Copy the web folder to S3 and refresh CloudFront.

Reads ApiUrl, WebBucketName, and CloudFrontDistributionId from the stack.
Writes the API URL into config.js so the browser can call API Gateway (CORS).

Run after sam deploy:

    python3 upload_web.py
"""

import json
import subprocess
import os

STACK_NAME = "employee-rating"
CONFIG_PATH = os.path.join("web", "config.js")
EMPTY_CONFIG = 'window.EMPLOYEE_API_BASE = "";\n'


def read_outputs():
    command = [
        "aws",
        "cloudformation",
        "describe-stacks",
        "--stack-name",
        STACK_NAME,
        "--query",
        "Stacks[0].Outputs",
        "--output",
        "json",
    ]
    raw = subprocess.check_output(command, text=True)
    items = json.loads(raw)
    result = {}
    i = 0
    while i < len(items):
        result[items[i]["OutputKey"]] = items[i]["OutputValue"]
        i = i + 1
    return result


def write_config(api_url):
    with open(CONFIG_PATH, "w") as file:
        file.write('window.EMPLOYEE_API_BASE = "' + api_url + '";\n')


def restore_config():
    with open(CONFIG_PATH, "w") as file:
        file.write(EMPTY_CONFIG)


def main():
    outputs = read_outputs()
    api_url = outputs["ApiUrl"]
    bucket = outputs["WebBucketName"]
    distribution_id = outputs["CloudFrontDistributionId"]
    website_url = outputs["WebsiteUrl"]

    print("API URL:", api_url)
    print("S3 bucket:", bucket)

    write_config(api_url)
    try:
        subprocess.check_call(
            ["aws", "s3", "sync", "web/", "s3://" + bucket + "/", "--delete"]
        )
        subprocess.check_call(
            [
                "aws",
                "cloudfront",
                "create-invalidation",
                "--distribution-id",
                distribution_id,
                "--paths",
                "/*",
            ]
        )
    finally:
        restore_config()

    print("Open this URL (CloudFront can take a few minutes the first time):")
    print(website_url)


if __name__ == "__main__":
    main()
