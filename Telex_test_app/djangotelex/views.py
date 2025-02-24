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
    """Fetch commits from GitHub and send report to Telex."""
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

            # Send fetched commits to Telex webhook
            send_telex_report()

        else:
            logger.error(f"Failed to fetch commits: {response.status_code}, {response.text}")

    except Exception as e:
        logger.error(f"Error fetching GitHub commits: {e}", exc_info=True)

"""def send_telex_report():
    Send a predefined report to Telex webhook.
    try:
        telex_webhook_url = os.getenv("TELEX_WEBHOOK_URL")
        if not telex_webhook_url:
            logger.error("Telex Webhook URL is not set in environment variables.")
            return

        logger.info(f"Preparing Telex report for {telex_webhook_url}")

        final_message = (
            "📌 *Repository Report:"
            "*\n🚨 *Error Logs:* No recent errors."
            "\n📊 *Performance:* Avg Response Time: 120ms, Slow Queries: 2"
            "\n🛠 *Code Quality:* Complexity Issues: 3, Code Smells: 5, Test Coverage: 85%"
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
                task_id = response.json().get("task_id", "unknown")
                logger.info(f"Telex accepted the request. Task ID: {task_id}")
            elif response.status_code == 200:
                logger.info("Successfully sent repo health report to Telex.")
            else:
                logger.error(f"Failed to send report to Telex: {response.status_code}, {response.text}")

    except Exception as e:
        logger.error(f"Error in send_telex_report: {e}", exc_info=True)"""
def send_telex_report():
    """Send a test report to Telex."""
    try:
        telex_webhook_url = os.getenv("TELEX_WEBHOOK_URL")
        
        if not telex_webhook_url:
            logger.error("Telex Webhook URL is not set.")
            return
        
        logger.info(f"Sending test report to {telex_webhook_url}")

        report_payload = {
            "message": "Test report from Django Telex APM.",
            "username": "Django Telex APM",
            "event_name": "Test Event",
            "status": "info"
        }

        logger.debug(f"Payload: {json.dumps(report_payload, indent=2)}")

        with httpx.Client() as client:
            response = client.post(telex_webhook_url, json=report_payload)

        logger.info(f"Response {response.status_code}: {response.text}")

    except Exception as e:
        logger.error(f"Error in send_telex_report: {e}", exc_info=True)

@csrf_exempt
def tick(request):
    """Trigger commit fetching and reporting."""
    try:
        data = json.loads(request.body or "{}")
        repo_name = data.get("repo_name", DEFAULT_REPO_NAME)
        token = data.get("token", DEFAULT_GITHUB_TOKEN)

        logger.info(f"Tick Triggered - Repo: {repo_name}, Token: {'***' if token else 'MISSING'}")

        threading.Thread(target=fetch_github_commits, args=(repo_name, token)).start()

        return JsonResponse({"status": "commit analysis started"}, status=202)

    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

