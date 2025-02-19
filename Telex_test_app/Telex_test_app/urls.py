from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path("djangotelex/", include("djangotelex.urls")),  # Include your app's URLs
]
