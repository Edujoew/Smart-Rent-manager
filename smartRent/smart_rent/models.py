from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Property(models.Model):
    name=models.CharField(max_length=200)
    landlord=models.ForeignKey(User, on_delete=models.CASCADE)
    address=models.CharField(max_length=300)

    def __str__(self):
        return self.name
class Tenant(models.Model):
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    property= models.ForeignKey(Property, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15) # For M-Pesa
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.user.get_full_name()

class UtilityBill(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    water_reading = models.FloatField()
    elecricity_reading = models.FloatField()
    billing_date = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)