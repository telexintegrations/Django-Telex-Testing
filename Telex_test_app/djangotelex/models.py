from django.db import models


class CommitLog(models.Model):
    commit_id = models.CharField(max_length=40, unique=True)
    author = models.CharField(max_length=100)
    message = models.TextField()
    timestamp = models.DateTimeField()
    url = models.URLField()
    modified_files = models.TextField()

    def __str__(self):
        return f"{self.author}: {self.message[:50]}"


class ErrorLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    error_message = models.TextField()
    traceback = models.TextField()
    level = models.CharField(max_length=10, choices=[("INFO", "INFO"), ("WARNING", "WARNING"), ("ERROR", "ERROR")])
    commit = models.ForeignKey(CommitLog, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.level} - {self.error_message[:50]}"
