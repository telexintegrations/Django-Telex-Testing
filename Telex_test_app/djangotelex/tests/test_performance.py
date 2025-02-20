import pytest
import time
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_performance_tracking():
    """Test if APM captures request time."""
 
    client = APIClient()
    url = reverse("get_errors")

    start_time = time.time()
    response = client.get(url)
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 2  # Ensuring response time is < 2s
