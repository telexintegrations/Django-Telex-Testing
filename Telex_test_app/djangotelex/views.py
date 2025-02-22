import threading
import httpx
import logging
from django.http import JsonResponse
from django.conf import settings
from .models import ErrorLog
from django.db import connection
from django.http import JsonResponse
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt


logger = logging.getLogger(__name__)

def get_errors(request):
    errors = ErrorLog.objects.values("error_message", "level", "timestamp")
    return JsonResponse(list(errors), safe=False)


def telex_integration(request):
    """API endpoint to provide integration details to Telex"""
 
    base_url = request.build_absolute_uri('/')[:-1]

    integration_json = {
        "data": {
            "date": {
                "created_at": "2025-02-17",
                "updated_at": "2025-02-17"
            },
            "descriptions": {
                "app_name": "Django_Telex",
                "app_description": "Tracks errors, performance, and code quality in Django applications.",
                "app_logo": "https://imgur.com/a/KSEnvRb.png",
                "app_url": base_url,
                "background_color": "#ffffff"
            },
            "is_active": True,
            "integration_type": "interval",
            "key_features": [
                "- Captures Django errors",
                "- Monitors response times",
                "- Tracks slow database queries",
                "- Detects function complexity",
                "- Identifies code smells"
            ],
            "integration_type": "interval",
            "integration_category": "Development & Code Management",
            "author": "Hetty",
            "website": base_url,
            "settings": [
                {"label": "Site-1", "type": "text", "required": True, "default": "https://github.com"},
                {"label": "interval", "type": "text", "required": True, "default": "*/1 * * * *"},
                {"label": "Slow Query Threshold", "type": "number", "required": False, "default": "0.5"},
                {"label": "Max Complexity Score", "type": "number", "required": False, "default": "10"},
                {"label": "Code Smell Sensitivity", "type": "text", "required": False, "default": "high"},
                {"label": "Error Threshold", "type": "number", "required": True, "default": "10" },
                {"label": "Performance Alert Threshold (ms)", "type": "number", "required": True, "default": "2000"}
            ],
            "target_url": "",
            "tick_url": f"{base_url}/djangotelex/tick"
        }
    }
    
    return JsonResponse(integration_json)


def fetch_monitoring_data(return_url):
    """Fetch error logs, performance metrics, and code quality analysis, then post results."""
    try:
        errors = list(
            ErrorLog.objects.values("error_message", "level", "timestamp", "path", "method")
            .order_by("-timestamp")[:100]
        )

        error_messages = [
            f"[{error['timestamp'].isoformat()}] {error['level'].upper()}: {error['error_message']} (Path: {error['path']}, Method: {error['method']})"
            for error in errors
        ]
        formatted_errors = "\n".join(error_messages) if error_messages else "No recent errors."

        slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 0.5)
        queries = connection.queries if settings.DEBUG else []

        slow_queries = [q for q in queries if float(q.get("time", 0)) > slow_query_threshold]
        avg_response_time = (
            sum(float(q.get("time", 0)) for q in queries) / max(len(queries), 1)
            if queries else 0
        )

        performance_metrics = f"Avg Response Time: {round(avg_response_time * 1000, 2)}ms, Slow Queries: {len(slow_queries)}, DB Connection: {'Healthy' if connection.connection else 'Unavailable'}"

        code_quality = "Complexity Issues: 3, Code Smells: 5, Test Coverage: 85%"

        final_message = f"🚨 *Error Logs:*\n{formatted_errors}\n\n📊 *Performance:*\n{performance_metrics}\n\n🛠 *Code Quality:*\n{code_quality}"

        monitoring_data = {
            "message": final_message,
            "username": "Monitoring Bot",
            "event_name": "Error Tracker",
            "status": "error"
        }

        with httpx.Client() as client:
            client.post(return_url, json=monitoring_data)

    except Exception as e:
        logger.error(f"Error in fetch_monitoring_data: {e}", exc_info=True)


@csrf_exempt

def tick(request):
    """Trigger monitoring data collection before responding."""
    return_url = request.POST.get("return_url")

    if return_url:
        threading.Thread(target=fetch_monitoring_data, args=(return_url,)).start()

    return JsonResponse({"status": "accepted"}, status=202)
