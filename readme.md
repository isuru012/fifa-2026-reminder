# FIFA 2026 Match Reminder

A Python + GitHub Actions project that automatically checks the FIFA World Cup 2026 fixtures page and sends match reminders through **ntfy**.

This project is designed so match reminders can still be sent even when your laptop is turned off. GitHub Actions runs the checker in the cloud every 15 minutes. When a match is close to kickoff, it sends a notification to an ntfy topic. Any phone, laptop, or browser subscribed to that topic can receive the reminder.

## Features

- Scrapes FIFA World Cup 2026 fixtures from the official FIFA fixtures page.
- Extracts match date, time, teams, stage/group/round, stadium, city, and match URL.
- Uses Sri Lanka time by default: `Asia/Colombo`.
- Runs automatically every 15 minutes using GitHub Actions.
- Sends reminders before kickoff using ntfy.
- Works on phones through the ntfy mobile app.
- Can also show laptop notifications if the laptop is subscribed to ntfy or running a local listener.

## How it works

```text
GitHub Actions runs every 15 minutes
        ↓
Python opens the FIFA fixtures page
        ↓
Python scrapes the latest fixture data
        ↓
Python checks if a match reminder is due
        ↓
Python sends a message to ntfy
        ↓
Phone/laptop receives the notification
```

## Important security note

Do **not** hard-code your personal ntfy topic inside public files.

Use a GitHub Actions secret named:

```text
NTFY_TOPIC
```

Your actual topic value should be stored only in GitHub Secrets.

This keeps the repository safe to publish publicly.

## Important limitation

GitHub Actions runs in the cloud. It cannot directly show a native Windows notification on your laptop.

For laptop notifications, use one of these options:

1. Open the ntfy topic in your browser and allow browser notifications.
2. Run a small local listener script on the laptop to show native Windows notifications.

If the laptop is turned off, laptop notifications will not work, but phone notifications will still work.

## Project structure

Your repository should look like this:

```text
fifa-2026-reminder/
│
├── fifa_reminder_cloud.py
├── requirements.txt
│
└── .github/
    └── workflows/
        └── fifa-reminder.yml
```

## Requirements

This project uses Python 3.11 or newer.

Python packages:

```txt
playwright
requests
beautifulsoup4
lxml
```

These packages are listed in `requirements.txt`.

## Files explanation

### `fifa_reminder_cloud.py`

Main Python script.

It:

- Opens the FIFA fixtures page with Playwright.
- Loads dynamic website content.
- Parses the HTML with BeautifulSoup.
- Extracts fixture details.
- Checks whether any match needs a reminder.
- Sends notifications through ntfy.

### `requirements.txt`

Contains the required Python packages.

### `.github/workflows/fifa-reminder.yml`

GitHub Actions workflow file.

It:

- Runs every 15 minutes.
- Installs Python.
- Installs project dependencies.
- Installs the Playwright Chromium browser.
- Runs `fifa_reminder_cloud.py`.

## Setup instructions

## 1. Create a GitHub repository

Create a GitHub repository, for example:

```text
fifa-2026-reminder
```

Then add these files:

```text
fifa_reminder_cloud.py
requirements.txt
.github/workflows/fifa-reminder.yml
```

Make sure the workflow file is exactly inside:

```text
.github/workflows/
```

GitHub Actions will not detect the workflow if the YAML file is in the wrong folder.

## 2. Create an ntfy topic

This project uses ntfy for notifications.

Create your own private/random ntfy topic name.

Example format:

```text
fifa2026_yourname_randomcode
```

For better privacy, use a hard-to-guess topic name, for example:

```text
fifa2026_user_92831_x7kq
```

Avoid simple public topic names like:

```text
fifa2026
```

Anyone who knows your public ntfy topic name may be able to send messages to it.

## 3. Subscribe on your phone

Install the ntfy app on your phone.

Then subscribe to your topic.

Example:

```text
fifa2026_user_92831_x7kq
```

Allow notifications when the phone asks.

## 4. Add the ntfy topic to GitHub Secrets

Go to your GitHub repository:

```text
Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Create this secret:

```text
Name: NTFY_TOPIC
Value: YOUR_PRIVATE_NTFY_TOPIC
```

Replace `YOUR_PRIVATE_NTFY_TOPIC` with your real ntfy topic.

Example:

```text
Name: NTFY_TOPIC
Value: fifa2026_user_92831_x7kq
```

The secret name must be exactly:

```text
NTFY_TOPIC
```

## 5. GitHub Actions workflow

Your workflow file should be located here:

```text
.github/workflows/fifa-reminder.yml
```

Example workflow:

```yaml
name: FIFA 2026 Match Reminder

on:
  schedule:
    # Every 15 minutes.
    # GitHub cron uses UTC time.
    - cron: "*/15 * * * *"

  workflow_dispatch:

jobs:
  remind:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Python packages
        run: pip install -r requirements.txt

      - name: Install Playwright browser
        run: python -m playwright install chromium

      - name: Run FIFA reminder checker
        env:
          NTFY_TOPIC: ${{ secrets.NTFY_TOPIC }}
          NTFY_SERVER: https://ntfy.sh
          REMIND_BEFORE_MINUTES: "30"
          CHECK_WINDOW_MINUTES: "15"
        run: python fifa_reminder_cloud.py
```

## How the reminder time works

The workflow runs every 15 minutes:

```yaml
- cron: "*/15 * * * *"
```

The Python script uses these values:

```text
REMIND_BEFORE_MINUTES = 30
CHECK_WINDOW_MINUTES = 15
```

That means:

- The reminder should be sent 30 minutes before kickoff.
- The script checks a 15-minute time window each time it runs.

Example:

```text
Match kickoff: 22:30
Reminder before: 30 minutes
Reminder target time: 22:00
GitHub Actions run: around 21:45–22:00
Notification sent
```

GitHub scheduled workflows may not run at the exact second, so the script uses a time window instead of one exact time.

## Change reminder time

To send reminders 60 minutes before kickoff, change this in `fifa-reminder.yml`:

```yaml
REMIND_BEFORE_MINUTES: "60"
```

To send reminders 15 minutes before kickoff:

```yaml
REMIND_BEFORE_MINUTES: "15"
```

## Change check interval

To run every 30 minutes, change the cron schedule:

```yaml
- cron: "*/30 * * * *"
```

Then also update:

```yaml
CHECK_WINDOW_MINUTES: "30"
```

Recommended default:

```yaml
REMIND_BEFORE_MINUTES: "30"
CHECK_WINDOW_MINUTES: "15"
```

## Test ntfy manually

Before testing GitHub Actions, test your ntfy topic.

Run this in Command Prompt, PowerShell, or terminal:

```bash
curl -d "Test FIFA notification" https://ntfy.sh/YOUR_PRIVATE_NTFY_TOPIC
```

Replace `YOUR_PRIVATE_NTFY_TOPIC` with your real topic.

Your phone should receive a notification.

## Test the project locally

Install dependencies:

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

Set the ntfy topic and run the script.

### Windows PowerShell

```powershell
$env:NTFY_TOPIC="YOUR_PRIVATE_NTFY_TOPIC"
python fifa_reminder_cloud.py
```

### Windows CMD

```cmd
set NTFY_TOPIC=YOUR_PRIVATE_NTFY_TOPIC
python fifa_reminder_cloud.py
```

### Linux/macOS

```bash
export NTFY_TOPIC=YOUR_PRIVATE_NTFY_TOPIC
python fifa_reminder_cloud.py
```

If no match is inside the reminder window, the script may print:

```text
No matches need reminders in this time window.
```

That is normal.

## Test GitHub Actions manually

Go to your repository on GitHub:

```text
Actions
→ FIFA 2026 Match Reminder
→ Run workflow
```

Check the workflow logs.

Normal output may include:

```text
Found 104 fixtures.
No matches need reminders in this time window.
```

or, when a reminder is due:

```text
Sending notification:
FIFA 2026: Team A vs Team B
Sent 1 notification(s).
```

## Laptop notifications

Phone notifications work directly with the ntfy app.

For laptop notifications, use one of the following methods.

## Option 1: Browser notifications

Open this URL in your laptop browser:

```text
https://ntfy.sh/YOUR_PRIVATE_NTFY_TOPIC
```

Allow browser notifications.

When GitHub Actions sends a notification, your browser can show it.

## Option 2: Native Windows notification listener

If you want native Windows toast notifications, create a separate local file on your laptop:

```text
laptop_ntfy_listener.py
```

Paste this code:

```python
import json
import os
import time
import requests
from winotify import Notification, audio


NTFY_SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")


def show_windows_notification(title, message):
    toast = Notification(
        app_id="FIFA 2026 Reminder",
        title=title,
        msg=message,
        duration="long",
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()


def listen_forever():
    if not NTFY_TOPIC:
        raise RuntimeError("Missing NTFY_TOPIC environment variable.")

    url = f"{NTFY_SERVER.rstrip('/')}/{NTFY_TOPIC}/json"

    while True:
        try:
            print(f"Listening: {url}")

            with requests.get(url, stream=True, timeout=90) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    event = json.loads(line.decode("utf-8"))

                    if event.get("event") != "message":
                        continue

                    title = event.get("title", "FIFA 2026 Reminder")
                    message = event.get("message", "")

                    show_windows_notification(title, message)

        except Exception as e:
            print(f"Error: {e}")
            print("Reconnecting in 10 seconds...")
            time.sleep(10)


if __name__ == "__main__":
    listen_forever()
```

Install packages:

```bash
pip install requests winotify
```

Run the listener.

### Windows PowerShell

```powershell
$env:NTFY_TOPIC="YOUR_PRIVATE_NTFY_TOPIC"
python laptop_ntfy_listener.py
```

### Windows CMD

```cmd
set NTFY_TOPIC=YOUR_PRIVATE_NTFY_TOPIC
python laptop_ntfy_listener.py
```

Now the laptop will show native Windows notifications when it is on and the listener is running.

## Start the laptop listener automatically on Windows

Create a batch file in the same folder as `laptop_ntfy_listener.py`:

```text
start_fifa_listener.bat
```

Paste this:

```bat
@echo off
cd /d "%~dp0"
set NTFY_TOPIC=YOUR_PRIVATE_NTFY_TOPIC
pythonw laptop_ntfy_listener.py
```

Replace `YOUR_PRIVATE_NTFY_TOPIC` with your own topic.

Then open the Windows Startup folder:

```text
Win + R
shell:startup
```

Copy `start_fifa_listener.bat` into that folder.

Now the listener will start automatically when Windows starts.

## Environment variables

The project uses these environment variables:

| Variable | Example | Meaning |
|---|---|---|
| `NTFY_TOPIC` | `YOUR_PRIVATE_NTFY_TOPIC` | ntfy topic used for notifications |
| `NTFY_SERVER` | `https://ntfy.sh` | ntfy server URL |
| `REMIND_BEFORE_MINUTES` | `30` | How many minutes before kickoff to send the reminder |
| `CHECK_WINDOW_MINUTES` | `15` | Time window checked by each GitHub Actions run |
| `DRY_RUN` | `false` | If `true`, prints notifications without sending them |

## Timezone

The project uses Sri Lanka time:

```python
LOCAL_TZ = ZoneInfo("Asia/Colombo")
```

Playwright also opens the FIFA page using the same timezone:

```python
timezone_id="Asia/Colombo"
```

## Troubleshooting

## GitHub Actions does not appear

Check that your workflow file is here:

```text
.github/workflows/fifa-reminder.yml
```

Also check that GitHub Actions is enabled for your repository.

## Error: Missing NTFY_TOPIC environment variable

This means the GitHub secret is missing or incorrect.

Check:

```text
Settings
→ Secrets and variables
→ Actions
```

The secret must be named:

```text
NTFY_TOPIC
```

## Phone does not receive notifications

Check:

- ntfy app is installed.
- You subscribed to the correct topic.
- Phone notifications are allowed.
- GitHub secret value matches the topic name exactly.
- Manual `curl` test works.

## Laptop does not show notifications

Check:

- The laptop is on.
- The browser topic page is open, or the listener script is running.
- Windows notifications are enabled.
- The ntfy topic in the listener script or environment variable matches your GitHub secret.

## Script finds zero fixtures

Possible reasons:

- FIFA changed the website layout.
- The page failed to load in GitHub Actions.
- The network request timed out.
- The scraper selectors need updating.

Check the GitHub Actions logs for errors.

## Script says no matches need reminders

This is usually normal.

It means no match is inside the current reminder window.

## Publishing this repository publicly

Before publishing the repository publicly, make sure:

- No real ntfy topic is hard-coded in the code.
- No `.env` file is committed.
- No personal token, password, API key, or secret is committed.
- The GitHub secret is stored only in repository settings.
- The README uses placeholder values like `YOUR_PRIVATE_NTFY_TOPIC`.

## License

This project is for personal and educational use.
