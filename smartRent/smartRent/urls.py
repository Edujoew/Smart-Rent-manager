from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Add this

urlpatterns = [
    path('admin/', admin.site.urls),
    
    
    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('', include('smart_rent.urls')),
]