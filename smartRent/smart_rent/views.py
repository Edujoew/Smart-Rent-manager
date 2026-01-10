from django.shortcuts import render, redirect, get_object_or_404
from .models import Tenant, UtilityBill
from django.contrib import messages

def dashboard(request):
    tenants = Tenant.objects.all()
    return render(request, 'smart_rent/dashboard.html', {'tenants': tenants})

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
            
            water_rate = 100 
            elec_rate = 25
            total_utility = (water * water_rate) + (electricity * elec_rate)
            total_bill = float(tenant.rent_amount) + total_utility
            
            messages.success(request, f"Bill generated for {tenant.user.get_full_name()}! Total: KES {total_bill}")
            return redirect('dashboard')
            
        except (ValueError, TypeError):
            messages.error(request, "Invalid input. Please enter numeric values for readings.")
            return redirect('generate_bill', tenant_id=tenant.id)
            
    return render(request, 'smart_rent/generate_bill.html', {'tenant': tenant})