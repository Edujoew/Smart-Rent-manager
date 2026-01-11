from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, UtilityBill, MpesaTransaction
from django.contrib import messages
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django_daraja.mpesa.core import MpesaClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import TenantRegistrationForm
from django.contrib.auth import logout as auth_logout
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User  
from .models import Tenant, Property         
from .models import Tenant, UtilityBill, Property
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PropertyForm, TenantRegistrationForm
from .models import Property, Tenant 

def is_landlord(user):
    return user.is_superuser or user.is_staff

def landing_page(request):
    if not request.user.is_authenticated:
        return render(request, 'smart_rent/landing.html')
    if is_landlord(request.user):
        return redirect('dashboard')
    return redirect('tenant_portal')

@login_required
@user_passes_test(is_landlord)
def dashboard(request):
    tenants = Tenant.objects.all()
    return render(request, 'smart_rent/dashboard.html', {'tenants': tenants})

@login_required
@user_passes_test(is_landlord)
def generate_bill(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        try:
            water = float(request.POST.get('water_reading', 0))
            electricity = float(request.POST.get('electricity_reading', 0))
            UtilityBill.objects.create(
                tenant=tenant,
                water_reading=water,
                elecricity_reading=electricity,
                is_paid=False
            )
            messages.success(request, f"Bill generated for {tenant.user.username}")
            return redirect('dashboard')
        except (ValueError, TypeError):
            messages.error(request, "Invalid input. Enter numeric values.")
            return redirect('generate_bill', tenant_id=tenant.id)
    return render(request, 'smart_rent/generate_bill.html', {'tenant': tenant})

@login_required
def tenant_portal(request):
    tenant = get_object_or_404(Tenant, user=request.user)
    unpaid_bills = UtilityBill.objects.filter(tenant=tenant, is_paid=False)
    all_bills = UtilityBill.objects.filter(tenant=tenant).order_by('-billing_date')
    
    # Calculate total due manually using the model property
    total_due = sum(bill.total_amount for bill in unpaid_bills)
    
    return render(request, 'smart_rent/tenant_portal.html', {
        'unpaid_bills': unpaid_bills,
        'bills': all_bills,
        'total_due': total_due,
        'tenant': tenant
    })

@login_required
def pay_bill(request, bill_id):
   
    bill = get_object_or_404(UtilityBill, id=bill_id)
    tenant = bill.tenant 

    if request.method == 'POST':
        
        phone_number = request.POST.get('phone').strip()
        amount = int(bill.total_amount)
        
        cl = MpesaClient()
        account_ref = f'BILL{bill.id}'
        desc = f'Rent Payment for {tenant.user.username}'
        callback_url = 'https://mydomain.com/mpesa-express-simulate/' 
        
        try:
            response = cl.stk_push(phone_number, amount, account_ref, desc, callback_url)
            
            if response.response_code == '0':
                MpesaTransaction.objects.create(
                    checkout_request_id=response.checkout_request_id,
                    phone_number=phone_number,
                    amount=amount,
                    bill=bill,
                    status='Pending'
                )
                
                return render(request, 'smart_rent/stk_push.html', {
                    'checkout_id': response.checkout_request_id,
                    'bill': bill
                })
            else:
                messages.error(request, f"M-Pesa Error: {response.response_description}")
                
        except Exception as e:
            messages.error(request, f"System Error: {str(e)}")
            
        
        if request.user.is_staff or request.user.is_superuser:
            return redirect('dashboard')
        return redirect('tenant_portal')
    
    
    return render(request, 'smart_rent/pay_confirm.html', {'bill': bill})

@login_required
@user_passes_test(is_landlord)
def unpaid_bills(request):
    bills = UtilityBill.objects.filter(is_paid=False)
    return render(request, 'smart_rent/unpaid_bills.html', {'bills': bills})

def check_payment_status(request, checkout_id):
    transaction = get_object_or_404(MpesaTransaction, checkout_request_id=checkout_id)
    return JsonResponse({'status': transaction.status})

def download_receipt(request, bill_id):
    bill = get_object_or_404(UtilityBill, id=bill_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{bill.id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "SMART RENT MANAGER - RECEIPT")
    p.drawString(100, 730, f"Tenant: {bill.tenant.user.username}")
    p.drawString(100, 710, f"Total: KES {bill.total_amount}")
    p.showPage()
    p.save()
    return response

def register(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please login.")
            return redirect('login')
    else:
        form = TenantRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('login')

@login_required
def add_tenant(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
           
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password='TempPassword123' 
            )
            
           
            tenant = form.save(commit=False)
            tenant.user = user
            tenant.save()
            
            return redirect('dashboard')
    else:
        form = TenantRegistrationForm()
    
    properties = Property.objects.all()
    return render(request, 'smart_rent/add_tenant.html', {
        'form': form, 
        'properties': properties
    })

@login_required
def dashboard(request):
    
    if not request.user.is_staff:
        return redirect('tenant_portal')
        
    tenants = Tenant.objects.all().select_related('property', 'user')
    properties_count = Property.objects.count()
    
    return render(request, 'smart_rent/dashboard.html', {
        'tenants': tenants,
        'properties_count': properties_count
    })



@login_required
@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
           
            property_obj = form.save(commit=False)
            
            property_obj.landlord = request.user 
            property_obj.save()
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'smart_rent/add_property.html', {'form': form})