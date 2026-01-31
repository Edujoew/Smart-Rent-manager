from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.admin.views.decorators import staff_member_required
from django_daraja.mpesa.core import MpesaClient
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import uuid

from .models import Tenant, UtilityBill, MpesaTransaction, Property, PropertyApplication, Payment
from .forms import PropertyForm, TenantRegistrationForm, UtilityBillForm, TenantUpdateForm 

def is_landlord(user):
    return user.is_superuser or user.is_staff

def landing_page(request):
    properties = Property.objects.all()
    category = request.GET.get('category')
    max_price = request.GET.get('max_price')

    if category:
        properties = properties.filter(category=category)
    
    if max_price:
        try:
            properties = properties.filter(price_per_month__lte=max_price)
        except ValueError:
            pass

    user_property_id = None
    if request.user.is_authenticated:
        try:
            tenant = Tenant.objects.get(user=request.user)
            if tenant.property:
                user_property_id = tenant.property.id
                properties = sorted(properties, key=lambda p: p.id != user_property_id)
        except Tenant.DoesNotExist:
            pass

    return render(request, 'smart_rent/landing.html', {
        'properties': properties,
        'user_property_id': user_property_id
    })

@login_required
def dashboard(request):
    applications = PropertyApplication.objects.filter(status='Pending')
    
    user_property_id = None
    if not request.user.is_staff:
        try:
            tenant = Tenant.objects.get(user=request.user)
            user_property_id = tenant.property.id if tenant.property else None
        except Tenant.DoesNotExist:
            pass

    context = {
        'properties': Property.objects.all(),
        'applications': applications if request.user.is_staff else None,
        'user_property_id': user_property_id,
    }
    return render(request, 'smart_rent/dashboard.html', context)

@login_required
@user_passes_test(is_landlord)
def tenant_list(request):
    tenants = Tenant.objects.all()
    return render(request, 'smart_rent/tenants_list.html', {'tenants': tenants})

@login_required
@user_passes_test(is_landlord)
def edit_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        form = TenantUpdateForm(request.POST, instance=tenant)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated details for {tenant.full_name or tenant.user.username}")
            return redirect('tenant_list')
    else:
        form = TenantUpdateForm(instance=tenant)
    
    return render(request, 'smart_rent/edit_tenant.html', {
        'form': form, 
        'tenant': tenant
    })

@login_required
@user_passes_test(is_landlord)
def generate_bill(request, tenant_id):
    tenant = get_object_or_404(Tenant, id=tenant_id)
    if request.method == 'POST':
        form = UtilityBillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.tenant = tenant
            bill.save() 
            messages.success(request, f"Bill of KES {bill.total_amount} generated for {tenant.user.username}")
            return redirect('tenant_list')
    else:
        form = UtilityBillForm()
    return render(request, 'smart_rent/generate_bill.html', {'form': form, 'tenant': tenant})

@login_required
def tenant_portal(request):
    try:
        tenant = Tenant.objects.get(user=request.user)
    except Tenant.DoesNotExist:
        messages.error(request, "You do not have a tenant profile. Are you logged in as a landlord?")
        return redirect('dashboard')

    bills = UtilityBill.objects.filter(tenant=tenant).order_by('-billing_date')
    unpaid_bills = bills.filter(is_paid=False)
    total_due = sum(bill.total_amount for bill in unpaid_bills)
    
    return render(request, 'smart_rent/tenant_portal.html', {
        'tenant': tenant,
        'bills': bills,
        'total_due': total_due,
    })

@login_required
def pay_bill(request, bill_id):
    bill = get_object_or_404(UtilityBill, id=bill_id)
    tenant = bill.tenant 
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone', '').strip()
        amount = int(bill.total_amount)
        cl = MpesaClient()
        
        try:
            response = cl.stk_push(phone_number, amount, f'BILL{bill.id}', f'Rent for {tenant.user.username}', 'https://mydomain.com/callback/')
            
            if response.response_code == '0':
                MpesaTransaction.objects.create(
                    checkout_request_id=response.checkout_request_id,
                    phone_number=phone_number,
                    amount=amount,
                    bill=bill,
                    status='Pending'
                )
                return render(request, 'smart_rent/stk_push.html', {'checkout_id': response.checkout_request_id, 'bill': bill})
        except Exception as e:
            messages.error(request, f"M-Pesa Error: {str(e)}")
            
        return redirect('tenant_portal')
    
    return render(request, 'smart_rent/pay_confirm.html', {'bill': bill})

@staff_member_required
def unpaid_bills(request):
    bills = UtilityBill.objects.filter(is_paid=False)
    return render(request, 'smart_rent/unpaid_bills.html', {'bills': bills})

@staff_member_required
def approve_application(request, app_id):
    application = get_object_or_404(PropertyApplication, id=app_id)
    if not User.objects.filter(email=application.email).exists():
        user = User.objects.create_user(
            username=application.email, 
            email=application.email,
            password=application.preferred_password,
            first_name=application.first_name,
            last_name=application.last_name
        )
        Tenant.objects.create(
            user=user, 
            property=application.property, 
            phone_number=application.phone_number,
            full_name=f"{application.first_name} {application.last_name}"
        )
        application.status = 'Approved'
        application.save()
        messages.success(request, f"Approved {application.first_name}!")
    return redirect('dashboard')

def apply_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id)
    if request.method == 'POST':
        PropertyApplication.objects.create(
            property=property_obj,
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone_number=request.POST.get('phone_number'),
            preferred_password=request.POST.get('password'), 
            status='Pending'
        )
        messages.success(request, "Application submitted!")
        return redirect('landing')
        
    return render(request, 'smart_rent/application_form.html', {'property': property_obj})

@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            property_obj = form.save(commit=False)
            property_obj.landlord = request.user 
            property_obj.save()
            return redirect('dashboard')
    else:
        form = PropertyForm()
    return render(request, 'smart_rent/add_property.html', {'form': form})

@login_required
def update_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = PropertyForm(instance=property_obj)
    return render(request, 'smart_rent/add_property.html', {'form': form, 'edit_mode': True})

@login_required
def delete_property(request, pk):
    property_obj = get_object_or_404(Property, pk=pk)
    if request.method == 'POST':
        property_obj.delete()
        return redirect('dashboard')
    return render(request, 'smart_rent/delete_confirm.html', {'object_name': property_obj.name})

@login_required
@user_passes_test(is_landlord)
def add_tenant(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=form.cleaned_data['email'],
                        email=form.cleaned_data['email'],
                        password=form.cleaned_data['password'],
                        first_name=form.cleaned_data['first_name'],
                        last_name=form.cleaned_data['last_name']
                    )
                    tenant = form.save(commit=False)
                    tenant.user = user 
                    tenant.full_name = f"{form.cleaned_data['first_name']} {form.cleaned_data['last_name']}"
                    tenant.save()
                return redirect('tenant_list')
            except Exception as e:
                form.add_error(None, f"Error: {e}")
    else:
        form = TenantRegistrationForm()
    return render(request, 'smart_rent/add_tenant.html', {'form': form})

@login_required
@user_passes_test(is_landlord)
def delete_tenant(request, pk):
    tenant = get_object_or_404(Tenant, pk=pk)
    if request.method == 'POST':
        tenant.delete()
        return redirect('tenant_list')
    return render(request, 'smart_rent/delete_confirm.html', {'object_name': tenant.user.username})

@login_required
def view_receipt(request, bill_id):
    if request.user.is_staff:
        bill = get_object_or_404(UtilityBill, id=bill_id)
    else:
        bill = get_object_or_404(UtilityBill, id=bill_id, tenant__user=request.user)
    return render(request, 'smart_rent/receipt_detail.html', {'bill': bill})

def download_receipt(request, bill_id):
    bill = get_object_or_404(UtilityBill, id=bill_id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Receipt_{bill.id}.pdf"'
    p = canvas.Canvas(response, pagesize=letter)
    p.drawString(100, 750, "SMART RENT MANAGER - RECEIPT")
    p.drawString(100, 730, f"Tenant: {bill.tenant.full_name or bill.tenant.user.username}")
    p.drawString(100, 710, f"Total: KES {bill.total_amount}")
    p.showPage()
    p.save()
    return response

def check_payment_status(request, checkout_id):
    transaction = get_object_or_404(MpesaTransaction, checkout_request_id=checkout_id)
    return JsonResponse({'status': transaction.status})

def register(request):
    if request.method == 'POST':
        form = TenantRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password']
            )
            tenant = form.save(commit=False)
            tenant.user = user
            tenant.save()
            return redirect('login')
    else:
        form = TenantRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('landing')

@login_required
@user_passes_test(is_landlord)
def clear_all_bills(request):
    if request.method == 'POST':
        updated_count = UtilityBill.objects.filter(is_paid=False).update(is_paid=True)
        messages.success(request, f"Successfully cleared {updated_count} bills. All tenants now show 'Account Fully Paid'.")
    return redirect('unpaid_bills')