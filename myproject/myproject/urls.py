from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # This maps everything in myapp.urls under the 'accounts/' path prefix
    path('accounts/', include('myapp.urls')),
    path('', include('myapp.urls')), # Or keep a direct root mapping if needed
]
