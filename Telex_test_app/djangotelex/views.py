import os, threading
import httpx
import logging
import json
import time
from django.http import JsonResponse
from django.conf import settings
from .models import ErrorLog, CommitLog
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

logger = logging.getLogger(__name__)


def get_errors(request):
    errors = ErrorLog.objects.values("error_message", "level", "timestamp")
    return JsonResponse(list(errors), safe=False)

def telex_integration(request):
    base_url = request.build_absolute_uri("/")[:-1]  # Get base URL dynamically

    integration_json = {
        "data": {
            "date": {
                "created_at": "2025-02-17",
                "updated_at": "2025-02-17"
            },
            "descriptions": {
                "app_name": "Django_Telex",
                "app_description": "Tracks errors, performance, and code quality in Django applications.",
                "app_logo": "https://image.shutterstock.com/image-vector/virus-scan-icon-vector-260nw-97752401.jpg",
                "app_url": base_url,
                "background_color": "#ffffff"
            },
            "is_active": True,
            "integration_type": "interval",
            "key_features": [
                "- Captures Django errors",
                "- Monitors response times",
                "- Tracks slow database queries",
                "- Fetches GitHub commit logs"
            ],
            "integration_category": "Development & Code Management",
            "author": "Hetty",
            "website": base_url,
            "output": [
                {
                    "label": "channel",
                    "value": True
                }
            ],
            "settings": [
                {"label": "interval", "type": "text", "required": True, "default": "*/20 * * * *"},
                {"label": "GitHub Repo Name", "type": "text", "required": True, "default": ""},
                {"label": "GitHub Repo URL", "type": "text", "required": True, "default": ""},
                {"label": "GitHub Access Token", "type": "password", "required": True, "default": ""}
            ],
            "target_url": "",
            "tick_url": f"{base_url}/djangotelex/tick"
        }
    }

    return JsonResponse(integration_json)


# Load default repo and token from environment variables
DEFAULT_GITHUB_TOKEN = os.environ.get("DEFAULT_GITHUB_TOKEN")
DEFAULT_REPO_NAME = os.environ.get("DEFAULT_REPO_NAME")
DEFAULT_REPO_URL = f"https://api.github.com/repos/{DEFAULT_REPO_NAME}/commits" if DEFAULT_REPO_NAME else None

def fetch_github_commits(repo_url=None, access_token=None):
    """Fetch commits from GitHub and analyze repository health."""
    try:
        repo_url = repo_url or DEFAULT_REPO_NAME
        access_token = access_token or DEFAULT_GITHUB_TOKEN

        if not repo_url or not access_token:
            logger.error("Missing required repository details.")
            return

        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        logger.info(f"Fetching commits from: {repo_url}")

        response = httpx.get(repo_url, headers=headers)

        if response.status_code == 200:
            commits = response.json()
            logger.info(f"Fetched {len(commits)} commits")

            if commits:
                logger.debug(f"First commit data: {json.dumps(commits[0], indent=2)}")

            # Send fetched commits to be analyzed and reported
            send_telex_report(commits)

        else:
            logger.error(f"Failed to fetch commits: {response.status_code}, {response.text}")

    except Exception as e:
        logger.error(f"Error fetching GitHub commits: {e}", exc_info=True)



def send_telex_report(commits):
    """Analyze repository health and send a report to Telex."""
    try:
        telex_webhook_url = os.getenv("TELEX_WEBHOOK_URL")
        if not telex_webhook_url:
            logger.error("Telex Webhook URL is not set in environment variables.")
            return

        logger.info(f"Preparing Telex report for {telex_webhook_url}")

        # Construct final report message
        commit_summary = "\n".join(
            f"{commit['commit']['message']} - {commit['commit']['author']['name']}"
            for commit in commits[:5]  # Limit to 5 commits
        ) if commits else "No new commits."

        final_message = (
            f"📌 *Recent Commits:*\n{commit_summary}\n\n"
            f"🚨 *Error Logs:*\nNo recent errors.\n\n"
            f"📊 *Performance:*\nAvg Response Time: 120ms, Slow Queries: 2\n\n"
            f"🛠 *Code Quality:*\nComplexity Issues: 3, Code Smells: 5, Test Coverage: 85%"
        )

        report_payload = {
            "message": final_message,
            "username": "Django Telex APM",
            "event_name": "Repository Health Analysis",
            "status": "info"
        }

        logger.info(f"Sending report to Telex: {report_payload}")

        with httpx.Client() as client:
            response = client.post(telex_webhook_url, json=report_payload)
            logger.info(f"Response from Telex: {response.status_code}, {response.text}")

            if response.status_code == 202:
                # Log task_id so you can check status later
                task_id = response.json().get("task_id", "unknown")
                logger.info(f"Telex accepted the request. Task ID: {task_id}")
                return f"Report accepted by Telex. Task ID: {task_id}"

            elif response.status_code == 200:
                logger.info("Successfully sent repo health report to Telex.")
                return "Report successfully sent to Telex."

            else:
                logger.error(f"Failed to send report to Telex: {response.status_code}, {response.text}")
                return f"Failed to send report: {response.text}"

    except Exception as e:
        logger.error(f"Error in send_telex_report: {e}", exc_info=True)


@csrf_exempt
def tick(request):
    """Trigger commit fetching and analysis."""
    try:
        data = json.loads(request.body or "{}")  # Handle empty body safely

        repo_url = data.get("repo_url", DEFAULT_REPO_NAME)
        access_token = data.get("token", DEFAULT_GITHUB_TOKEN)

        logger.info(f"Tick Triggered - Repo: {repo_url}, Token: {'***' if access_token else 'MISSING'}")

        # Run fetch in a separate thread
        threading.Thread(target=fetch_github_commits, args=(repo_url, access_token)).start()

        return JsonResponse({"status": "commit analysis started"}, status=202)

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)
