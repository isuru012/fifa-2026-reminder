# FIFA 2026 Match Reminder

A Python project that checks the FIFA World Cup 2026 fixtures page and sends match reminders using **ntfy**.

The script runs automatically in **GitHub Actions** every 15 minutes. When a match is close to kickoff, it sends a notification to your ntfy topic. Your phone, browser, or laptop listener can receive the reminder.

## Features

- Scrapes FIFA 2026 fixtures.
- Uses Sri Lanka time: `Asia/Colombo`.
- Runs every 15 minutes with GitHub Actions.
- Sends notifications through ntfy.
- Works even when your laptop is off.
- Optional Windows native notification support using a local listener.

## Project Structure

```text
fifa-2026-reminder/
│
├── fifa_reminder_cloud.py
├── laptop_ntfy_listener.py
├── requirements.txt
├── readme.md
└── .github/
    └── workflows/
        └── fifa-reminder.yml
```

## Requirements

```txt
playwright
requests
beautifulsoup4
lxml
tzdata
winotify
```

`winotify` is only needed for the optional Windows laptop listener.

## Setup

### 1. Install dependencies locally

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

### 2. Create an ntfy topic

Create your own private/random ntfy topic, for example:

```text
fifa2026_yourname_randomcode
```

Do not hard-code your real topic in public code.

### 3. Add GitHub Secret

In your GitHub repository:

```text
Settings → Secrets and variables → Actions → New repository secret
```

Add:

```text
Name: NTFY_TOPIC
Value: YOUR_PRIVATE_NTFY_TOPIC
```

## GitHub Actions

The workflow file must be here:

```text
.github/workflows/fifa-reminder.yml
```

Example schedule:

```yaml
on:
  schedule:
    - cron: "*/15 * * * *"
  workflow_dispatch:
```

This runs the reminder checker every 15 minutes. You can also run it manually from the **Actions** tab.

## Run Locally

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

If no match is close to kickoff, this output is normal:

```text
No matches need reminders in this time window.
```

## Test ntfy

```bash
curl -d "Test FIFA notification" https://ntfy.sh/YOUR_PRIVATE_NTFY_TOPIC
```

Your phone should receive a test notification.

## Optional: Windows Native Notifications

Run `laptop_ntfy_listener.py` on your Windows laptop to receive native Windows notifications.

Install:

```bash
pip install requests winotify
```

Run:

```powershell
$env:NTFY_TOPIC="YOUR_PRIVATE_NTFY_TOPIC"
python laptop_ntfy_listener.py
```

This only works when the laptop is on and the listener is running.

## Timing

Default behavior:

```text
REMIND_BEFORE_MINUTES = 30
CHECK_WINDOW_MINUTES = 15
```

This means the script sends a reminder around 30 minutes before kickoff and checks every 15 minutes.

To change the reminder time, edit the environment values in `fifa-reminder.yml`.

## Important Notes

- Do not publish your real ntfy topic.
- Store the real topic only in GitHub Secrets.
- If FIFA changes their website layout, the scraper may need updates.
- GitHub Actions cannot directly show Windows notifications; use ntfy or the laptop listener.

## License

Personal and educational use.
