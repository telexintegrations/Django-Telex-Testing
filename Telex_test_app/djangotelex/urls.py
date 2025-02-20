from django.urls import path
from .views import get_errors
from .views import telex_integration


urlpatterns = [
    path("errors/", get_errors, name="get_errors"),
    path("integration.json", telex_integration, name="telex_integration"),
]
