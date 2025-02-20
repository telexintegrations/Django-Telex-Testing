
from django.http import JsonResponse
from .models import ErrorLog
import datetime


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
            "tick_url": f"{base_url}/tick"
        }
    }
    
    return JsonResponse(integration_json)


def tick(request):
    """Fetches and returns error logs, performance metrics, and code quality results."""
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