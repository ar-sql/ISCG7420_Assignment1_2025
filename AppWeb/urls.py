# AppWeb/urls.py

from django.urls import path, include

urlpatterns = [
    # no built‐in admin; all routes live in reservations.urls
    path('', include('reservations.urls')),
]
