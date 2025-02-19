from django.apps import AppConfig
from django.db.utils import OperationalError

class DjangotelexConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'djangotelex'


class DjangotelexConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "djangotelex"

    def ready(self):
        from djangotelex.models import ErrorLog
        from datetime import datetime

        try:
            ErrorLog.objects.create(
                error_message="Server started test error",
                level="info",
                timestamp=datetime.now()
            )
        except OperationalError:
            # Prevents issues if migrations haven't been applied yet
            pass
