from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    CATEGORY_CHOICES = [
        ('1-Bedroom Apartment', '1-Bedroom Apartment'),
        ('2-Bedroom Apartment', '2-Bedroom Apartment'),
        ('3-Bedroom Apartment', '3-Bedroom Apartment'),
        ('Executive/Serviced Apartment', 'Executive/Serviced Apartment'),
        ('Bungalow', 'Bungalow'),
        ('Maisonette', 'Maisonette'),
        ('Townhouse', 'Townhouse'),
        ('Villa', 'Villa'),
        ('Student Hostel/Housing', 'Student Hostel/Housing'),
        ('Airbnb/Short-Term Rental', 'Airbnb/Short-Term Rental'),
    ]

    name = models.CharField(max_length=200)
    landlord = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=300)
    category = models.CharField(
        max_length=100, 
        choices=CATEGORY_CHOICES, 
        default="2-Bedroom Apartment"
    ) 
    price_per_month = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='property_pics/', default='default_house.jpg', null=True, blank=True)
    # Added to track availability in the landlord dashboard
    is_occupied = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Tenant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # This link is what allows you to change "Unassigned" to a house name
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=200, blank=True) # Added to display names like "John Shikoli"
    phone_number = models.CharField(max_length=15)
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Auto-fill rent from property price if not specified
        if self.property and (self.rent_amount == 0 or self.rent_amount is None):
            self.rent_amount = self.property.price_per_month
        
        # Logic to mark property as occupied when assigned
        if self.property:
            self.property.is_occupied = True
            self.property.save()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name if self.full_name else self.user.username

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

class Payment(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    bill = models.OneToOneField(UtilityBill, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_reference = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, default='M-Pesa')
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.transaction_reference} - {self.tenant.user.username}"

class MpesaTransaction(models.Model):
    checkout_request_id = models.CharField(max_length=100, unique=True)
    bill = models.ForeignKey('UtilityBill', on_delete=models.CASCADE, null=True)
    phone_number = models.CharField(max_length=15)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.checkout_request_id} - {self.status}"

class PropertyApplication(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    preferred_password = models.CharField(max_length=128) 
    status = models.CharField(max_length=20, default='Pending') 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.property.name}"