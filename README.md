# Django Telex APM

Django Telex APM is an application performance monitoring (APM) tool for Django applications. It captures and logs errors, performance metrics, slow queries, and code quality insights, providing real-time feedback on your backend's health.

## Features
- **Error Logging**: Captures errors with timestamps, request paths, methods, and tracebacks.
- **Performance Monitoring**: Tracks request response times.
- **Slow Query Detection**: Logs database queries that exceed a configurable threshold.
- **Code Quality Analysis**: Reports complexity issues, code smells, and test coverage statistics.
- **Automated API Endpoint**: Call `/djangotelex/tick` to retrieve the latest logs and metrics.

## Installation
### Prerequisites
- Python 3.x
- Django

### Setup
1. **Clone the repository:**
   ```sh
   git clone https://github.com/telexintegrations/Django-Telex-Testing.git
   cd Telex_test_app
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
3. **Apply migrations:**
   ```sh
   python manage.py migrate
   ```
4. **Run the server:**
   ```sh
   python manage.py runserver
   ```

## Configuration
Modify `settings.py` to include middleware:
```python
MIDDLEWARE = [
    ...
    'djangotelex.middleware.PerformanceMonitoringMiddleware',
    'djangotelex.middleware.SlowQueryMiddleware',
]

SLOW_QUERY_THRESHOLD = 0.5  # Adjust the threshold for slow queries (in seconds)
```

## API Usage
### Send a Tick Request
To retrieve performance and error logs, send a `POST` request to:
```sh
curl -X POST http://127.0.0.1:8000/djangotelex/tick -H "Content-Type: application/json"
```
#### Example Response
```json
{
    "errors": [
        {"error_message": "Test error", "level": "critical", "timestamp": "2025-02-19T11:21:15.386Z", "path": "", "method": ""}
    ],
    "performance": {
        "avg_response_time": 0.2,
        "slow_queries": 1,
        "db_connection_status": "healthy"
    },
    "code_quality": {
        "complexity_issues": 3,
        "code_smells": 5,
        "test_coverage": "85%"
    },
    "status": "success"
}
```

## Testing
### Error Logging Test
Trigger an error manually by raising an exception in a Django view:
```python
from django.http import JsonResponse

def test_error(request):
    raise Exception("This is a test error")
```
Call the endpoint:
```sh
curl -X GET http://127.0.0.1:8000/test-error/
```
Then check `/djangotelex/tick` to see if the error appears.

### Slow Query Test
Create a slow query test endpoint:
```python
import time
from django.db import connection
from django.http import JsonResponse

def slow_query_test(request):
    time.sleep(2)  # Simulate a slow request
    with connection.cursor() as cursor:
        cursor.execute("SELECT pg_sleep(1);")  # PostgreSQL example
    return JsonResponse({"message": "Slow query test completed"})
```
Call the endpoint:
```sh
curl -X GET http://127.0.0.1:8000/slow-query-test/
```
Then check `/djangotelex/tick` for slow query logs.

## Roadmap
- Add support for distributed tracing
- Enhance visualization dashboard for logs and metrics
- Integrate AI-based anomaly detection

## License
This project is licensed under the MIT License.

## Contributions
Pull requests are welcome! Please follow the contribution guidelines before submitting changes.

## Author
[Henrietta Onoge](https://github.com/Samuelhetty)
