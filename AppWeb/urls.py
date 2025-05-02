# AppWeb/urls.py

from django.urls import path, include

urlpatterns = [
    # All application routes in reservations.urls
    path('', include('reservations.urls')),

    # If you still need Django's built-in admin, mount it here:
    # from django.contrib import admin
    # path('django-admin/', admin.site.urls),
]
