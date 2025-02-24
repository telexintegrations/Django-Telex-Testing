# Django Telex APM

Django Telex APM is an **Application Performance Monitoring (APM) tool** that integrates with Django to track errors, performance metrics, slow database queries, and code quality. It sends monitoring reports to a configured Telex webhook.

## Features
- 📌 **Error Tracking:** Captures Django application errors with timestamps and request details.
- 🚀 **Performance Monitoring:** Tracks response times and identifies slow database queries.
- 🔍 **Code Quality Analysis:** Detects function complexity, code smells, and test coverage.
- 🌐 **Webhook Integration:** Sends monitoring reports to **Telex webhooks** for easy tracking.

---

## Installation
### 1️⃣ **Clone the Repository**
```bash
 git clone https://github.com/Samuelhetty/Django-Telex-Error-tracking-Apm.git
 cd Django-Telex-Error-tracking-Apm
```

### 2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 3️⃣ **Configure Environment Variables**
Create a `.env` file in the project root and add:
```env
TELEX_WEBHOOK_URL=https://ping.telex.im/v1/webhooks/YOUR_WEBHOOK_ID
SLOW_QUERY_THRESHOLD=0.5
DEBUG=True
```

Replace `YOUR_WEBHOOK_ID` with the actual webhook URL from Telex.

---

## Usage
### 🔹 **Start the Django Server**
```bash
python manage.py runserver
```

### 🔹 **Trigger Monitoring Data Collection**
Use the `/djangotelex/tick` endpoint to initiate the monitoring process:
```bash
curl -X POST http://127.0.0.1:8000/djangotelex/tick
```
_Response:_
```json
{"status": "accepted"}
```

### 🔹 **Check Integration Details**
Visit `/djangotelex/integration.json` in your browser:
```
http://127.0.0.1:8000/djangotelex/integration.json
```
This will return the integration details in JSON format.

---

## API Endpoints
| Endpoint                     | Method | Description |
|------------------------------|--------|-------------|
| `/djangotelex/tick`          | POST   | Triggers monitoring data collection and sends reports to Telex. |
| `/djangotelex/integration.json` | GET    | Returns integration metadata about the monitoring service. |
| `/djangotelex/get_errors`    | GET    | Fetches a list of recent errors stored in the database. |

---

## How It Works
1. **Error Tracking:** Captures application errors and logs them into the `ErrorLog` model.
2. **Performance Monitoring:** Measures slow queries and response times from Django’s database connection.
3. **Code Quality Metrics:** Simulates static analysis for complexity, test coverage, and code smells.
4. **Webhook Reporting:** Formats collected data into a report and sends it to the configured Telex webhook.

---

## Example Monitoring Report
A sample report sent to the webhook might look like:
```json
{
    "message": "🚨 *Error Logs:*\nNo recent errors.\n\n📊 *Performance:*\nAvg Response Time: 120ms, Slow Queries: 2, DB Connection: Healthy\n\n🛠 *Code Quality:*\nComplexity Issues: 3, Code Smells: 5, Test Coverage: 85%",
    "username": "Django Tracker",
    "event_name": "Reports",
    "status": "error"
}
```

---

## Author
👤 **Hetty**

---

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Contributions
Contributions are welcome! Feel free to fork the repository and submit a pull request.

---

## Author
[Henrietta Onoge](https://github.com/Samuelhetty)