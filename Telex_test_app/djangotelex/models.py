from django.db import models


class ErrorLog(models.Model):
    LOG_LEVELS = [
        ("info", "Info"),
        ("warning", "Warning"),
        ("error", "Error"),
        ("critical", "Critical"),
    ]
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    error_message = models.TextField()
    traceback = models.TextField()
    level = models.CharField(max_length=10, choices=LOG_LEVELS,
                             default="error")

    def __str__(self):
        return f"{self.timestamp} - {self.path} - {self.error_message[:50]}"
