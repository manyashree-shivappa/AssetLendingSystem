from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # Enables /accounts/login/, /accounts/logout/, etc.
    path('accounts/', include('django.contrib.auth.urls')),
    # Connects your app's urls
    path('', include('myapp.urls')),
]
