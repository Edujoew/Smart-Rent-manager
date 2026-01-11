from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    
    path('', views.landing_page, name='landing'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('my-portal/', views.tenant_portal, name='tenant_portal'), 
    
    path('generate-bill/<int:tenant_id>/', views.generate_bill, name='generate_bill'),
    path('unpaid-bills/', views.unpaid_bills, name='unpaid_bills'),
    path('pay/<int:bill_id>/', views.pay_bill, name='pay_bill'),
    path('receipt/<int:bill_id>/', views.download_receipt, name='download_receipt'),
    path('check-status/<str:checkout_id>/', views.check_payment_status, name='check_payment_status'),
    path('my-portal/', views.tenant_portal, name='tenant_portal'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/add-tenant/', views.add_tenant, name='add_tenant'),
    path('dashboard/add-property/', views.add_property, name='add_property'),
]