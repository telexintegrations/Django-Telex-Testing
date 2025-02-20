from django.urls import path
from .views import get_errors, telex_integration, tick


urlpatterns = [
    path("errors/", get_errors, name="get_errors"),
    path("integration.json", telex_integration, name="telex_integration"),
    path("tick", tick, name="tick"),
]
