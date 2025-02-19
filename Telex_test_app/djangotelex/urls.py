from django.urls import path
from .views import get_errors
from .views import telex_integration
from .views import djangotelex_home, get_errors, telex_integration

urlpatterns = [
    path("", djangotelex_home, name="djangotelex_home"),  # Default route for /djangotelex/
    path("errors/", get_errors, name="get_errors"),
    path("integration.json", telex_integration, name="telex_integration"),
]
