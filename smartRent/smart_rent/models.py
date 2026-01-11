from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    name = models.CharField(max_length=200)
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=300)
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return self.name
class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True)
    phone_number = models.CharField(max_length=15)
    
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        
        if self.property and (self.rent_amount == 0 or self.rent_amount is None):
            self.rent_amount = self.property.price_per_month
        super().save(*args, **kwargs)

class UtilityBill(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    water_reading = models.FloatField()
    elecricity_reading = models.FloatField()
    billing_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    @property
    def total_amount(self):
        water_cost = self.water_reading * 100
        elec_cost = self.elecricity_reading * 25
        return float(self.tenant.rent_amount) + water_cost + elec_cost

    def __str__(self):
        return f"Bill for {self.tenant.user.username} - {self.billing_date}"

class MpesaTransaction(models.Model):
    checkout_request_id = models.CharField(max_length=100, unique=True)
    bill = models.ForeignKey('UtilityBill', on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.checkout_request_id} - {self.status}"

