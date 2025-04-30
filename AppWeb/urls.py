from django.contrib import admin
from django.urls    import path, include

urlpatterns = [
    path('admin/',    admin.site.urls),

    # Your app’s URLs
    path('',          include('reservations.urls')),

    # Django’s built-in auth (login, logout, password reset)
    path('accounts/', include('django.contrib.auth.urls')),
]
