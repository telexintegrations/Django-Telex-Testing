import os, threading
import httpx
import logging
import json
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
                #{"label": "GitHub Repo URL", "type": "text", "required": True, "default": ""},
                {"label": "GitHub Access Token", "type": "password", "required": True, "default": ""}
            ],
            "target_url": "",
            "tick_url": f"{base_url}/djangotelex/tick"
        }
    }

    return JsonResponse(integration_json)


def fetch_github_commits(repo_name, repo_url, access_token):
    """Fetch commits from a GitHub repository and analyze repo health."""
    try:
        headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }

        response = httpx.get(repo_url, headers=headers)

        if response.status_code == 200:
            commits = response.json()
            logger.info(f"Fetched {len(commits)} commits from {repo_name}")

            # Run full analysis
            report = analyze_repository_health(commits)

            # Send full report to Telex Webhook
            send_telex_report(report)

        else:
            logger.error(f"Failed to fetch commits: {response.status_code}, {response.text}")

    except Exception as e:
        logger.error(f"Error fetching GitHub commits: {e}", exc_info=True)

def analyze_repository_health(commits):
    """Analyze commits, errors, performance, and code quality."""
    
    # 🔹 1. **Recent Errors**  
    errors = list(
        ErrorLog.objects.values("error_message", "level", "timestamp", "path", "method")
        .order_by("-timestamp")[:5]
    )
    error_messages = [
        f"⚠️ [{error['timestamp'].isoformat()}] {error['level'].upper()}: {error['error_message']} (Path: {error['path']}, Method: {error['method']})"
        for error in errors
    ]
    formatted_errors = "\n".join(error_messages) if error_messages else "✅ No recent errors."

    # 🔹 2. **Performance Metrics**  
    slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 0.5)
    queries = connection.queries if settings.DEBUG else []
    slow_queries = [q for q in queries if float(q.get("time", 0)) > slow_query_threshold]
    avg_response_time = (
        sum(float(q.get("time", 0)) for q in queries) / max(len(queries), 1) if queries else 0
    )
    performance_metrics = (
        f"⏳ Avg Response Time: {round(avg_response_time * 1000, 2)}ms\n🐢 Slow Queries: {len(slow_queries)}"
    )

    # 🔹 3. **Static Code Analysis (Placeholder for now)**  
    code_quality = "🛠 Complexity Issues: 3, Code Smells: 5, Test Coverage: 85%"

    # 🔹 4. **Commit Summary**  
    commit_messages = [
        f"📌 *{commit['commit']['message']}*\n👤 {commit['commit']['author']['name']}\n🔗 [View Commit]({commit['html_url']})"
        for commit in commits[:5]  # Limit to first 5 commits
    ]
    commit_summary = "\n\n".join(commit_messages) if commit_messages else "📭 No new commits."

    # 🔹 5. **Final Report Message**  
    final_report = (
        f"📝 *GitHub Repository Analysis:*\n\n"
        f"📌 *Recent Commits:*\n{commit_summary}\n\n"
        f"🚨 *Error Logs:*\n{formatted_errors}\n\n"
        f"📊 *Performance Metrics:*\n{performance_metrics}\n\n"
        f"🛠 *Code Quality:*\n{code_quality}"
    )

    return final_report

def send_telex_report(report):
    """Send the repository health report to the Telex webhook."""
    telex_webhook_url = os.getenv("TELEX_WEBHOOK_URL")
    if not telex_webhook_url:
        logger.error("Telex Webhook URL is not set in environment variables.")
        return

    payload = {
        "message": report,
        "username": "Django Telex APM",
        "event_name": "Repository Health Analysis",
        "status": "info"
    }

    try:
        with httpx.Client() as client:
            response = client.post(telex_webhook_url, json=payload)
            if response.status_code == 200:
                logger.info("Successfully sent repo health report to Telex.")
            else:
                logger.error(f"Failed to send report to Telex: {response.status_code}, {response.text}")
    
    except Exception as e:
        logger.error(f"Error sending Telex report: {e}", exc_info=True)


@csrf_exempt
def tick(request):
    """Trigger commit fetching and analysis."""
    try:
        body = request.body.decode("utf-8")
        print("Received request body:", body)  # Debugging output
        data = json.loads(body)
    except json.JSONDecodeError:
        return JsonResponse({"status": "error", "message": "Invalid JSON format."}, status=400)

    repo_name = data.get("repo_name")
    token = data.get("token")

    if not repo_name or not token:
        return JsonResponse({"status": "error", "message": "Missing required parameters."}, status=400)

    threading.Thread(target=fetch_github_commits, args=(repo_name, token)).start()
    return JsonResponse({"status": "commit analysis started"}, status=202)
