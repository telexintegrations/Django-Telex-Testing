import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from djangotelex.models import ErrorLog
from django.utils.timezone import now

@pytest.mark.django_db
def test_get_errors():
    """Test if API returns logged errors properly."""
    
    client = APIClient()

    # Insert test error
    ErrorLog.objects.create(
        error_message="API test error",
        level="warning",
        timestamp=now()
    )

    url = reverse("get_errors")  
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["error_message"] == "API test error"
