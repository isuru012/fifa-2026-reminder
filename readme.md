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
