# Django Telex APM

Django Telex APM is an Application Performance Monitoring (APM) tool that tracks **errors, performance, slow queries, and code quality** in a Django backend. It integrates with **GitHub repositories** to analyze commits and sends reports to a **Telex webhook**.

## Features
- **Error Tracking**: Captures and reports errors logged in Django.
- **Performance Monitoring**: Tracks slow queries and response times.
- **Code Quality Analysis**: Analyzes commit changes for code complexity and test coverage.
- **GitHub Integration**: Fetches commits on demand and processes them for issues.
- **Telex Webhook Reporting**: Sends reports to a configured Telex webhook.

---

## Installation

### 1. Clone the Repository
```sh
$ git clone "https://github.com/telexintegrations/Django-Telex-Testing.git"
$ cd Telex_test_app
```

### 2. Set Up a Virtual Environment
```sh
$ python -m venv venv
$ source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```sh
$ pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a **.env** file and add the following:
```env
GITHUB_ACCESS_TOKEN=your_github_token
TELEX_WEBHOOK_URL=your_telex_webhook_url
SLOW_QUERY_THRESHOLD=0.5  # (optional, in seconds)
DEBUG=True  # Set to False in production
```

---

## Usage

### 1. Run Migrations
```sh
$ python manage.py migrate
```

### 2. Start the Server
```sh
$ python manage.py runserver
```

### 3. Test the APM
You can test the commit analysis and error monitoring by making a **POST request** to the `/djangotelex/tick` endpoint.

#### Using cURL
```sh
curl -X POST "https://django-telex-testing.onrender.com/djangotelex/tick" \
     -H "Content-Type: application/json" \
     -d '{"repo_name": "YOUR_USERNAME/YOUR_REPO", "token": "YOUR_GITHUB_TOKEN"}'
```

#### Using Postman
1. Open **Postman**.
2. Select **POST** as the method.
3. Enter the URL: `https://django-telex-testing.onrender.com/djangotelex/tick`
4. Go to the **Body** tab → Select **raw** → Choose **JSON** format.
5. Enter the payload:
   ```json
   {
      "repo_name": "YOUR_USERNAME/YOUR_REPO",
      "token": "YOUR_GITHUB_TOKEN"
   }
   ```
6. Click **Send**.

### 4. Expected Response
```json
{
    "status": "commit analysis started"
}
```

If everything is set up correctly, you should receive a **report** in your Telex webhook channel containing **error logs, performance insights, and code quality analysis**.

---

## Troubleshooting

### 1. No Message in Telex Webhook
- Ensure `TELEX_WEBHOOK_URL` is correctly set in `.env`.
- Test manually:
  ```sh
  curl -X POST "YOUR_TELEX_WEBHOOK_URL" -H "Content-Type: application/json" -d '{"message": "Test message", "username": "Django APM"}'
  ```

### 2. GitHub API Returns 403 (Forbidden)
- Ensure your **GitHub token** has the required permissions:
  - `repo`
  - `contents`
  - `workflow`
  - `admin:repo_hook`

- Test manually:
  ```sh
  curl -H "Authorization: token YOUR_GITHUB_TOKEN" \
       -H "Accept: application/vnd.github.v3+json" \
       https://api.github.com/repos/YOUR_USERNAME/YOUR_REPO/commits
  ```

### 3. Django Shows CSRF Verification Error
- Use **Postman** or **cURL** with the `-H "X-CSRFToken"` header.
- Alternatively, disable CSRF verification in `views.py` (for testing only):
  ```python
  from django.views.decorators.csrf import csrf_exempt
  @csrf_exempt
  def tick(request):
      ...
  ```

---

## Contributing
1. Fork the repo.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -m "Add new feature"`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

---

## License
This project is licensed under the **MIT License**.

---

## Contributions
Pull requests are welcome! Please follow the contribution guidelines before submitting changes.

## Author
[Henrietta Onoge](https://github.com/Samuelhetty)