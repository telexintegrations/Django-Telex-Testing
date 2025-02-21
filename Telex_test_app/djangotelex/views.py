
from django.http import JsonResponse, FileResponse
from django.conf import settings
from .models import ErrorLog
import datetime
import logging, requests


# Create a logger instance
logger = logging.getLogger(__name__)

TELEX_WEBHOOK_URL = getattr(settings, "TELEX_WEBHOOK_URL", "https://ping.telex.im/v1/webhooks/01951330-037c-7b3f-98d3-ac3cbdea30c5")

def get_logo():
    return FileResponse("Track_logo.jpg")


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
                {"label": "interval", "type": "text", "required": True, "default": "*****"},
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

"""
def tick(request):
    Fetches and returns error logs, performance metrics, and code quality results.
    if request.method == "GET":
        errors = list(ErrorLog.objects.values("error_message", "level", "timestamp"))

        performance_metrics = {
            "avg_response_time": 120,
            "slow_queries": 3,
            "complexity_issues": 5
        }

        response_data = {
            "errors": errors,
            "performance": performance_metrics,
            "status": "success"
        }

        return JsonResponse(response_data, safe=False)

    return JsonResponse({"error": "Method not allowed"}, status=405)
    """
TELEX_WEBHOOK_URL = settings.TELEX_WEBHOOK_URL  # Ensure this is defined in settings.py
"""
def tick(request):
    Fetches and returns error logs, performance metrics, and code quality results.
    if request.method == "GET":
        try:
            # Get the latest error logs
            errors = list(ErrorLog.objects.values("error_message", "level", "timestamp"))

            # Mock performance metrics (Replace with real data if available)
            performance_metrics = {
                "avg_response_time": 120,  # in milliseconds
                "slow_queries": 3,
                "complexity_issues": 5
            }

            # Combine data for response and webhook
            response_data = {
                "errors": errors,
                "performance": performance_metrics,
                "status": "success"
            }

            # Send data to Telex Webhook
            try:
                response = requests.post(TELEX_WEBHOOK_URL, json=response_data, timeout=5)
                response.raise_for_status()  # Raise an error for bad responses (4xx, 5xx)
                logger.info("Successfully sent data to Telex webhook")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send data to Telex webhook: {e}")

            # Ensure the response is JSON with proper content type
            return JsonResponse(response_data, safe=False, content_type="application/json")

        except Exception as e:
            logger.error(f"Error in tick function: {e}")
            return JsonResponse({"error": "Internal Server Error"}, status=500, content_type="application/json")

    return JsonResponse({"error": "Method not allowed"}, status=405, content_type="application/json")

    """

def tick(request):
    """Fetches and returns error logs, performance metrics, and code quality results."""
    
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        # Fetch the latest error logs safely
        errors = list(ErrorLog.objects.values("error_message", "level", "timestamp")) if ErrorLog.objects.exists() else []

        # Mock performance metrics (Replace with real data if available)
        performance_metrics = {
            "avg_response_time": 120,  # in milliseconds
            "slow_queries": 3,
            "complexity_issues": 5
        }

        # Response payload
        response_data = {
            "errors": errors,
            "performance": performance_metrics,
            "status": "success"
        }

        # Send data to Telex Webhook (only if URL is set)
        if TELEX_WEBHOOK_URL:
            try:
                response = requests.post(TELEX_WEBHOOK_URL, json=response_data, timeout=5)
                response.raise_for_status()  # Ensure it's a successful request
                logger.info("Successfully sent data to Telex webhook")
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to send data to Telex webhook: {e}")
        
        return JsonResponse(response_data, safe=False, content_type="application/json")

    except Exception as e:
        logger.error(f"Unexpected error in tick: {e}", exc_info=True)
        return JsonResponse({"error": "Internal Server Error", "details": str(e)}, status=500, content_type="application/json")