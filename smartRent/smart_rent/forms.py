from django import forms
from .models import UtilityBill

class BillGenerationForm(forms.ModelForm):
    class Meta:
        model = UtilityBill
        fields = ['water_reading', 'elecricity_reading']
        widgets = {
            'water_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter water units'}),
            'elecricity_reading': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter electricity units'}),
        }