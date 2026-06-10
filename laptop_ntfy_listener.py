import json
import time
import requests
from winotify import Notification, audio


import os

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
            print(f"Listening for FIFA reminders: {url}")

            with requests.get(url, stream=True, timeout=90) as response:
                response.raise_for_status()

                for line in response.iter_lines():
                    if not line:
                        continue

                    try:
                        event = json.loads(line.decode("utf-8"))
                    except json.JSONDecodeError:
                        continue

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