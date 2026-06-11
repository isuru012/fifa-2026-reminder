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