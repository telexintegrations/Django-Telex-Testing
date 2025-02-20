import pytest
from djangotelex.models import ErrorLog
from django.utils.timezone import now


@pytest.mark.django_db
def test_error_logging():
    """Test if an error is successfully logged in the database."""
 
    error = ErrorLog.objects.create(
        error_message="Test error",
        level="critical",
        timestamp=now()
    )

    # Fetch the logged error
    saved_error = ErrorLog.objects.get(id=error.id)

    assert saved_error.error_message == "Test error"
    assert saved_error.level == "critical"
    assert saved_error.timestamp is not None
