from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('generate-bill/<int:tenant_id>/', views.generate_bill, name='generate_bill'),
]