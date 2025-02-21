import logging
import time
import traceback
from django.http import JsonResponse
from django.utils.timezone import now
from django.db import connection
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from djangotelex.models import ErrorLog

logger = logging.getLogger(__name__)

class ErrorTrackingMiddleware:
    """Middleware to track and log application errors"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Store error in database
            ErrorLog.objects.create(
                timestamp=now(),
                path=request.path,
                method=request.method,
                error_message=str(e),
                traceback=traceback.format_exc(),
            )

            # Log error to a file
            logger.error(f"Error at {request.path}: {e}\n{traceback.format_exc()}")

            # Return JSON error response
            return JsonResponse(
                {"status": "error", "error_message": "An internal error occurred."}, status=500
            )




class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to track request processing time"""

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - request.start_time
        logger.info(f"Request to {request.path} [{request.method}] took {duration:.4f} seconds")
        return response


class SlowQueryMiddleware(MiddlewareMixin):
    """Middleware to log slow queries"""

    def process_request(self, request):
        request.start_time = time.time()

    def process_response(self, request, response):
        execution_time = time.time() - request.start_time
        slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 0.5)

        for query in connection.queries:
            query_time = float(query.get("time", 0))
            if query_time > slow_query_threshold:
                logger.warning(
                    f"Slow Query on {request.path} [{request.method}]: {query['sql']} took {query_time}s"
                )

        return response

"""
class PerformanceAndQueryMiddleware(MiddlewareMixin):
    Middleware to track request processing time and log slow queries

    def process_request(self, request):
        request._start_time = time.time()

    def process_response(self, request, response):
        duration = time.time() - request._start_time
        slow_query_threshold = getattr(settings, "SLOW_QUERY_THRESHOLD", 0.5)

        # Log request performance
        logger.info(
            f"Request to {request.path} [{request.method}] by {getattr(request, 'user', 'Anonymous')} "
            f"took {duration:.4f} seconds - Status: {response.status_code}"
        )

        # Log slow queries
        for query in connection.queries:
            query_time = float(query.get("time", 0))
            if query_time > slow_query_threshold:
                logger.warning(
                    f"Slow Query on {request.path} [{request.method}]: {query['sql']} took {query_time}s"
                )

        return response
        """