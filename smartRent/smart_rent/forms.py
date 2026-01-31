from django import forms
from django.contrib.auth.models import User
from .models import UtilityBill, Property, Tenant

class BillGenerationForm(forms.ModelForm):
    class Meta:
        model = UtilityBill
        fields = ['water_reading', 'elecricity_reading']
        widgets = {
            'water_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter water units'}),
            'elecricity_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter electricity units'}),
        }

class TenantRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    
    password = forms.CharField(
        label="Set Tenant Password", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Create a password for tenant'})
    )
    confirm_password = forms.CharField(
        label="Confirm Tenant Password", 
        widget=forms.PasswordInput(attrs={'placeholder': 'Confirm the password'})
    )

    class Meta:
        model = Tenant
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'password', 
            'confirm_password', 
            'property', 
            'phone_number', 
            'rent_amount'
        ]
        widgets = {
            'rent_amount': forms.NumberInput(attrs={'id': 'id_rent_amount'}),
            'property': forms.Select(attrs={'id': 'id_property'}),
        }

class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['name', 'price_per_month']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Riverside Apartment A1'}),
            'price_per_month': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 15000'}),
        }

class UtilityBillForm(forms.ModelForm):
    class Meta:
        model = UtilityBill
        fields = ['water_reading', 'elecricity_reading']
        widgets = {
            'water_reading': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter water units used'
            }),
            'elecricity_reading': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Enter electricity units used'
            }),
        }

class TenantUpdateForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['full_name', 'property', 'phone_number', 'rent_amount']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'property': forms.Select(attrs={'class': 'form-select'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 0712345678'}),
            'rent_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }