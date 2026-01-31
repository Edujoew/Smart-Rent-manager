import os
import django
import requests
from django.core.files.base import ContentFile

# 1. Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartRent.settings')
django.setup()

from smart_rent.models import Property
from django.contrib.auth.models import User

def add_ten_new_properties():
    # Get the landlord (superuser)
    landlord = User.objects.first()
    if not landlord:
        print("Error: No superuser found. Run 'python manage.py createsuperuser' first.")
        return

    # Data for 10 new Kenyan-style properties
    new_data = [
        ("The Grand Oasis", "High Class", 250000, "Runda, Nairobi", "mansion"),
        ("Pinnacle Heights", "High Class", 190000, "Upper Hill, Nairobi", "luxury-apartment"),
        ("Thika Greens Villa", "High Class", 130000, "Thika", "modern-house"),
        ("Greenwood Apartments", "Middle Class", 65000, "Kiambu Road", "apartment-building"),
        ("Sunset Estate", "Middle Class", 45000, "Ngong, Kajiado", "townhouse"),
        ("Unity Homes", "Middle Class", 50000, "Tatu City, Ruiru", "suburban-home"),
        ("Mwangaza Court", "Low Class", 12000, "Zimmerman, Nairobi", "bedsitter-interior"),
        ("Baraka Apartments", "Low Class", 9500, "Roysambu, Nairobi", "studio-apartment"),
        ("Juja South Suites", "Student Pockets", 6000, "Juja", "dormitory-room"),
        ("Kenyatta Road Singles", "Student Pockets", 4500, "Kenyatta Road", "small-room")
    ]

    print("--- Starting Property Injection ---")

    for name, cat, price, addr, kw in new_data:
        # Avoid duplicates if you run the script twice
        prop, created = Property.objects.get_or_create(
            name=name,
            defaults={
                'category': cat,
                'price_per_month': price,
                'landlord': landlord,
                'address': addr
            }
        )

        if created:
            # Download a realistic real estate image for each
            # Using keyword-based architecture source to match your pool theme
            img_url = f"https://source.unsplash.com/800x600/?architecture,building,interior,{kw}"
            try:
                response = requests.get(img_url, timeout=15)
                if response.status_code == 200:
                    file_name = f"{name.replace(' ', '_')}.jpg"
                    prop.image.save(file_name, ContentFile(response.content), save=True)
                    print(f"SUCCESS: Created {name} with image.")
                else:
                    print(f"CREATED: {name} (Image download failed)")
            except Exception as e:
                print(f"CREATED: {name} (Error fetching image: {e})")
        else:
            print(f"SKIPPED: {name} already exists in database.")

    print("--- Finished Adding 10 Properties ---")

if __name__ == '__main__':
    add_ten_new_properties()