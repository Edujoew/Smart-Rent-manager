from django.contrib import admin
from .models import Property, Tenant, UtilityBill

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('name', 'landlord', 'address')
    search_fields = ('name', 'address')

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    # This lets you see the rent and phone number without clicking the tenant
    list_display = ('user', 'property', 'phone_number', 'rent_amount')
    list_filter = ('property',)
    search_fields = ('user__username', 'phone_number')

@admin.register(UtilityBill)
class UtilityBillAdmin(admin.ModelAdmin):
    # This helps you track who has paid and who hasn't
    list_display = ('tenant', 'billing_date', 'is_paid')
    list_filter = ('is_paid', 'billing_date')