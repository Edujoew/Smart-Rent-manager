from django import forms
from .models import UtilityBill
from .models import Property
from .models import Tenant
from django.contrib.auth.models import User
from .models import Tenant, Property




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
    
    class Meta:
        model = Tenant
       
        fields = ['property', 'phone_number', 'rent_amount']
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