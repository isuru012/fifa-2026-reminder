import os
import re
import sys
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from playwright.sync_api import sync_playwright

from bs4 import BeautifulSoup
from datetime import datetime
from zoneinfo import ZoneInfo

LOCAL_TZ = ZoneInfo("Asia/Colombo")

FIFA_URL = "https://www.fifa.com/en/tournaments/mens/worldcup/canadamexicousa2026/scores-fixtures?country=&wtw-filter=ALL"


def get_text(el):
    if not el:
        return ""
    return " ".join(el.get_text(" ", strip=True).split())

# Send notification around 30 minutes before kickoff.
REMIND_BEFORE_MINUTES = int(os.getenv("REMIND_BEFORE_MINUTES", "30"))

# GitHub Actions runs every 15 minutes.
# We send reminders for matches whose reminder time is inside the next 15 minutes.
CHECK_WINDOW_MINUTES = int(os.getenv("CHECK_WINDOW_MINUTES", "15"))

NTFY_SERVER = os.getenv("NTFY_SERVER", "https://ntfy.sh")
NTFY_TOPIC = os.getenv("NTFY_TOPIC")

DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"


def log(message):
    print(message, flush=True)


def parse_date_line(line):
    pattern = (
        r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+"
        r"\d{1,2}\s+"
        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+"
        r"2026$"
    )

    if not re.match(pattern, line):
        return None

    return datetime.strptime(line, "%A %d %B %Y").date()


def is_time_line(line):
    return re.fullmatch(r"\d{2}:\d{2}", line.strip()) is not None


def is_match_line_with_time(line):
    return re.search(r"\b\d{2}:\d{2}\b", line) is not None


def clean_text(line):
    return re.sub(r"\s+", " ", line).strip()


def is_bad_team_text(line):
    bad_words = [
        "view brackets",
        "tickets",
        "match schedule",
        "scores",
        "fixtures",
        "fifa",
        "privacy",
        "cookies",
        "sign in",
        "shop",
    ]

    low = line.lower()

    if any(word in low for word in bad_words):
        return True

    if len(line) > 80:
        return True

    return False


def extract_round_and_venue(lines, start_index):
    round_text = ""
    venue = ""

    for j in range(start_index, min(start_index + 8, len(lines))):
        line = clean_text(lines[j])

        if not line:
            continue

        if "Stadium" in line or "Final" in line or "Round" in line or "Group" in line:
            parts = re.split(r"\s+·\s+|\s+\.\s+", line)

            if len(parts) >= 2:
                round_text = parts[0].strip()
                venue = parts[1].strip()
            else:
                round_text = line.strip()

            break

    return round_text, venue


def scrape_fifa_fixtures():
    fixtures = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--single-process",
                "--no-zygote",
            ],
        )

        context = browser.new_context(
            timezone_id="Asia/Colombo",
            locale="en-US",
            viewport={"width": 1920, "height": 1080},
        )

        page = context.new_page()

        def block_unneeded(route):
            if route.request.resource_type in ["image", "font", "media"]:
                route.abort()
            else:
                route.continue_()

        page.route("**/*", block_unneeded)

        log("Opening FIFA page...")
        page.goto(FIFA_URL, wait_until="domcontentloaded", timeout=120000)

        log("Waiting for fixtures to appear...")
        page.wait_for_selector('[class*="matches-container_title"]', timeout=120000)
        # Scroll to load all fixtures
        for _ in range(40):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(500)

        html = page.content()
        browser.close()

    soup = BeautifulSoup(html, "lxml")

    # Each big date section
    date_sections = soup.select("div.col-xl-12.col-lg-12.ff-pb-24.ff-text-blue-dark")

    for section in date_sections:
        date_el = section.select_one('[class*="matches-container_title"]')
        if not date_el:
            continue

        date_text = get_text(date_el)

        try:
            match_date = datetime.strptime(date_text, "%A %d %B %Y").date()
        except ValueError:
            continue

        # Each match link inside this date section
        match_links = section.select('a[href*="/match-centre/match/"]')

        for match_link in match_links:
            time_el = match_link.select_one('[class*="match-row_matchTime"]')
            if not time_el:
                continue

            time_text = get_text(time_el)

            team_els = match_link.select('[class*="match-row_team"] span.d-none.d-md-block')

            if len(team_els) < 2:
                continue

            home = get_text(team_els[0])
            away = get_text(team_els[1])

            bottom_labels = [
                get_text(x)
                for x in match_link.select('[class*="match-row_bottomLabel"]')
                if get_text(x)
            ]

            stage = bottom_labels[0] if len(bottom_labels) >= 1 else ""
            group_or_round = bottom_labels[1] if len(bottom_labels) >= 2 else ""

            stadium_city_spans = [
                get_text(x)
                for x in match_link.select('[class*="match-row_stadiumCityLabels"] span')
                if get_text(x)
            ]

            stadium = stadium_city_spans[0] if len(stadium_city_spans) >= 1 else ""
            city = stadium_city_spans[1] if len(stadium_city_spans) >= 2 else ""

            kickoff_local = datetime.strptime(
                f"{match_date} {time_text}",
                "%Y-%m-%d %H:%M"
            ).replace(tzinfo=LOCAL_TZ)

            match_url = match_link.get("href", "")
            if match_url.startswith("/"):
                match_url = "https://www.fifa.com" + match_url

            fixtures.append({
                "date": str(match_date),
                "time": time_text,
                "home": home,
                "away": away,
                "stage": stage,
                "group_or_round": group_or_round,
                "stadium": stadium,
                "city": city,
                "venue": f"{stadium} {city}".strip(),
                "kickoff_local": kickoff_local,
                "match_url": match_url,
            })

    # Remove duplicates by match URL if possible
    unique = {}

    for fixture in fixtures:
        key = fixture["match_url"] or (
            f"{fixture['date']}|{fixture['time']}|"
            f"{fixture['home']}|{fixture['away']}|{fixture['stadium']}"
        )
        unique[key] = fixture

    fixtures = list(unique.values())

    print(f"Found {len(fixtures)} fixtures.")
    return fixtures

def should_notify(kickoff_local):
    now = datetime.now(LOCAL_TZ)

    reminder_time = kickoff_local - timedelta(minutes=REMIND_BEFORE_MINUTES)

    window_start = now
    window_end = now + timedelta(minutes=CHECK_WINDOW_MINUTES)

    return window_start <= reminder_time < window_end


def send_ntfy_notification(title, message, click_url=None):
    if not NTFY_TOPIC:
        raise RuntimeError("Missing NTFY_TOPIC environment variable.")

    url = f"{NTFY_SERVER.rstrip('/')}/{NTFY_TOPIC}"

    headers = {
        "Title": title,
        "Priority": "high",
        "Tags": "soccer",
    }

    if click_url:
        headers["Click"] = click_url

    if DRY_RUN:
        log("DRY RUN: notification not sent")
        log(title)
        log(message)
        return

    response = requests.post(
        url,
        data=message.encode("utf-8"),
        headers=headers,
        timeout=30,
    )

    response.raise_for_status()


def main():
    now = datetime.now(LOCAL_TZ)
    log(f"Current Sri Lanka time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    fixtures = scrape_fifa_fixtures()

    sent_count = 0

    for fixture in fixtures:
        kickoff = fixture["kickoff_local"]

        if should_notify(kickoff):
            title = f"FIFA 2026: {fixture['home']} vs {fixture['away']}"

            message = (
                f"{fixture['home']} vs {fixture['away']}\n"
                f"Kickoff: {kickoff.strftime('%A %d %B %Y, %H:%M')} Sri Lanka time\n"
                f"{fixture.get('stage', '')} {fixture.get('group_or_round', '')}\n"
                f"{fixture.get('stadium', '')} {fixture.get('city', '')}\n\n"
                f"Reminder: {REMIND_BEFORE_MINUTES} minutes before kickoff"
            )

            log("Sending notification:")
            log(title)
            log(message)

            send_ntfy_notification(
                title=title,
                message=message,
                click_url=fixture.get("match_url") or FIFA_URL,
            )

            sent_count += 1

    if sent_count == 0:
        log("No matches need reminders in this time window.")
    else:
        log(f"Sent {sent_count} notification(s).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log(f"ERROR: {e}")
        sys.exit(1)