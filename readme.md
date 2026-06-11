# FIFA 2026 Match Reminder

A Python reminder project for FIFA World Cup 2026 matches.

The project checks the FIFA fixtures page, finds matches that are close to kickoff, and sends a notification using **ntfy**.

This version runs in the cloud using:

```text
Amazon EventBridge Scheduler -> AWS Lambda Docker container -> Python reminder script -> ntfy notification
```

## Features

- Checks FIFA 2026 match fixtures.
- Uses Sri Lanka time: `Asia/Colombo`.
- Sends reminders through ntfy.
- Runs automatically every 15 minutes on AWS.
- Works even when the laptop is turned off.
- Optional Windows laptop listener for native Windows notifications.

## Final Cloud Setup

The current setup uses AWS instead of GitHub Actions:

```text
AWS ECR
Stores the Docker image.

AWS Lambda
Runs the Docker image and executes fifa_reminder_cloud.py.

Amazon EventBridge Scheduler
Starts the Lambda function every 15 minutes.

ntfy
Receives the reminder notification.
```

## Project Structure

```text
fifa-2026-reminder/
│
├── fifa_reminder_cloud.py
├── lambda_handler.py
├── laptop_ntfy_listener.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .env.example
└── readme.md
```

## Requirements

Main cloud requirements:

```txt
playwright
requests
beautifulsoup4
lxml
tzdata
```

Optional Windows laptop notification requirement:

```txt
winotify
```

## Environment Variables

Create a `.env.example` file with example values only:

```env
NTFY_TOPIC=your_ntfy_topic_here
NTFY_SERVER=https://ntfy.sh
REMIND_BEFORE_MINUTES=15
CHECK_WINDOW_MINUTES=15
```

Do not commit your real ntfy topic, AWS keys, or local credentials.

## Timing

The final setup uses:

```text
REMIND_BEFORE_MINUTES=15
CHECK_WINDOW_MINUTES=15
EventBridge schedule=rate(15 minutes)
```

Meaning:

```text
Every 15 minutes, AWS runs the checker.
The checker looks for matches starting within the next 15 minutes.
If a match is found, it sends a reminder through ntfy.
```
## Docker Setup

The Docker image uses the Playwright Python base image.

Example `Dockerfile`:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt awslambdaric

COPY . .

ENTRYPOINT ["/usr/bin/python3", "-m", "awslambdaric"]

CMD ["lambda_handler.lambda_handler"]
```

## Lambda Handler

`lambda_handler.py` runs the main checker script inside Lambda:

```python
import subprocess
import sys


def lambda_handler(event, context):
    result = subprocess.run(
        [sys.executable, "fifa_reminder_cloud.py"],
        capture_output=True,
        text=True,
        timeout=840
    )

    print("STDOUT:")
    print(result.stdout)

    print("STDERR:")
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Script failed with code {result.returncode}")

    return {
        "statusCode": 200,
        "body": "FIFA reminder check completed"
    }
```

## Build And Push Docker Image

Login to AWS ECR:

```powershell
aws ecr get-login-password --region ap-south-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com
```

Build and push:

```powershell
docker buildx build `
  --platform linux/amd64 `
  --provenance=false `
  -t YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/fifa-reminder:latest `
  --push `
  .
```

`--provenance=false` is important because AWS Lambda may reject unsupported Docker image manifest formats.

## Create Lambda Function

Create the Lambda function from the ECR Docker image:

```powershell
aws lambda create-function `
  --function-name fifa-reminder `
  --package-type Image `
  --code ImageUri=YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/fifa-reminder:latest `
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/fifa-reminder-lambda-role `
  --timeout 900 `
  --memory-size 1024 `
  --region ap-south-1 `
  --environment "Variables={NTFY_TOPIC=YOUR_PRIVATE_NTFY_TOPIC,NTFY_SERVER=https://ntfy.sh,REMIND_BEFORE_MINUTES=15,CHECK_WINDOW_MINUTES=15}"
```

After the function is created, do not run `create-function` again.

For future updates, use:

```powershell
aws lambda update-function-code `
  --function-name fifa-reminder `
  --image-uri YOUR_ACCOUNT_ID.dkr.ecr.ap-south-1.amazonaws.com/fifa-reminder:latest `
  --region ap-south-1
```

## Test Lambda Manually

Run:

```powershell
aws lambda invoke `
  --function-name fifa-reminder `
  --region ap-south-1 `
  output.json
```

Check:

```powershell
type output.json
```

Successful output:

```json
{"statusCode": 200, "body": "FIFA reminder check completed"}
```

## Create Automatic 15-Minute Schedule

In AWS Console:

```text
Amazon EventBridge -> Scheduler -> Create schedule
```

Use:

```text
Schedule name: fifa-reminder-every-15-minutes
Schedule pattern: Recurring schedule
Schedule type: Rate-based schedule
Rate expression: 15 minutes
Flexible time window: Off
Target: AWS Lambda
Lambda function: fifa-reminder
Payload: {}
```

Important: create the schedule in the same AWS region as Lambda:

```text
Asia Pacific (Mumbai) ap-south-1
```

## Check Cloud Logs

To check recent Lambda logs:

```powershell
aws logs tail /aws/lambda/fifa-reminder `
  --region ap-south-1 `
  --since 30m
```

You can also check:

```text
AWS Console -> CloudWatch -> Log groups -> /aws/lambda/fifa-reminder
```

## Optional Windows Laptop Listener

The AWS Lambda sends ntfy notifications. If you also want native Windows notifications on your laptop, run:

```powershell
python laptop_ntfy_listener.py
```

The laptop listener only works while the laptop is turned on.

To run the listener hidden at Windows startup, use a local `.vbs` startup file with `pythonw.exe`. Do not commit that file to GitHub because it contains local paths.

## Test ntfy

Send a test message:

```powershell
curl -d "Test FIFA notification" https://ntfy.sh/YOUR_PRIVATE_NTFY_TOPIC
```

Your phone or listener should receive the notification.

## Important Notes

- Keep private values in environment variables, not directly in the code.
- Do not commit AWS access keys, `.env` files, local logs, virtual environments, or machine-specific startup scripts.
- Use `.env.example` to show other users which values they need to configure.
- If FIFA changes their website layout, the scraper may need updates.
- GitHub Actions is no longer required for the main cloud schedule.

## License

Personal and educational use.
