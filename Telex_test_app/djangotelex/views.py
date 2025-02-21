import json
import logging
import requests
from django.http import JsonResponse
from datetime import datetime
from django.conf import settings
from .models import ErrorLog
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db import connection



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


@csrf_exempt  # Allows external calls if needed
@require_POST  # Ensures only POST requests are accepted


def tick(request):
    """Fetches error logs, performance metrics, and code quality analysis.
       Sends results to a return_url if provided.
    """
    try:
        # Get latest error logs and convert timestamp to string
        errors = list(
            ErrorLog.objects.values("error_message", "level", "timestamp", "path", "method")
        )
        
        # Convert `timestamp` field to ISO format
        for error in errors:
            if isinstance(error["timestamp"], datetime):
                error["timestamp"] = error["timestamp"].isoformat()

        # Extract performance metrics
        slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 0.5)
        slow_queries = [
            query for query in connection.queries if float(query.get("time", 0)) > slow_query_threshold
        ]
        avg_response_time = sum(float(q.get("time", 0)) for q in connection.queries) / max(len(connection.queries), 1)

        performance_metrics = {
            "avg_response_time": round(avg_response_time * 1000, 2),  # Convert to milliseconds
            "slow_queries": len(slow_queries),
            "db_connection_status": "healthy" if connection.connection else "unavailable"
        }

        # Mock Code Quality Analysis
        code_quality = {
            "complexity_issues": 3,   
            "code_smells": 5,
            "test_coverage": "85%"
        }

        # Combine all data
        response_data = {
            "errors": errors,
            "performance": performance_metrics,
            "code_quality": code_quality,
            "status": "success"
        }

        # Check if return_url is provided in the request body
        if request.method == "POST" and request.body:
            try:
                body = json.loads(request.body.decode("utf-8"))
                return_url = body.get("return_url")

                if return_url:
                    response = requests.post(return_url, json=response_data, timeout=5)
                    logger.info(f"Return URL response: {response.status_code}, {response.text}")

            except json.JSONDecodeError:
                logger.error("Invalid JSON in request body.")
            except requests.RequestException as e:
                logger.error(f"Failed to send data to return_url: {e}")

        return JsonResponse(response_data, safe=False, status=202)

    except Exception as e:
        logger.error(f"Unexpected error in tick: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)