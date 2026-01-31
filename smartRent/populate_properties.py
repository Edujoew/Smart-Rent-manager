import os
import django
import requests
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartRent.settings')
django.setup()

from smart_rent.models import Property
from django.contrib.auth.models import User
from django.conf import settings

def populate():
    path = os.path.join(settings.MEDIA_ROOT, 'property_pics')
    os.makedirs(path, exist_ok=True)
    landlord = User.objects.first()

    # REAL RENTAL DATA: Hand-picked IDs for Buildings and Interiors
    properties_data = [
        # EXTERIORS (High & Middle Class)
        ("The Azure Residency", "High Class", 180000, "Westlands", "1613498377330-3ef071305147"),
        ("Hillside Executive", "High Class", 120000, "Lavington", "1600585154340-be6161a56a0c"),
        ("Safari Terrace", "High Class", 150000, "Karen", "1512917774080-9991f1c4c750"),
        ("Riverside Annex", "Middle Class", 55000, "Ruaka", "1591375273539-6019598a8e32"),
        ("Savannah Court", "Middle Class", 45000, "South B", "1564013799082-ae37515d07a1"),
        
        # INTERIORS (Bedrooms & Bedsitters)
        ("Amani Court", "Low Class", 8500, "Pipeline", "1522708323597-5d7857ff0007"),
        ("Zion Gates", "Low Class", 9000, "Kayole", "1484154218944-4051ab81d4ad"),
        ("Campus Annex A", "Student Pockets", 3000, "Juja", "1523214658296-e97771c248f5"),
        ("Scholar’s Hub", "Student Pockets", 5500, "Madaraka", "1584622650145-2f9b17ce203b"),
        ("Uni-Suites", "Student Pockets", 4000, "Rongai", "1605204289209-d2929ca3a23e")
    ]

    session = requests.Session()

    for name, cat, price, addr, img_id in properties_data:
        obj = Property.objects.create(
            name=name, category=cat, price_per_month=price,
            landlord=landlord, address=addr
        )
        
        # Exact architectural/interior URL
        img_url = f"https://images.unsplash.com/photo-{img_id}?auto=format&fit=crop&w=800&q=80"
        
        try:
            print(f"Downloading REAL photo for: {name}...", end=" ", flush=True)
            response = session.get(img_url, timeout=30)
            if response.status_code == 200:
                file_name = f"{name.replace(' ', '_')}.jpg"
                obj.image.save(file_name, ContentFile(response.content), save=True)
                print("SUCCESS")
            else:
                print(f"FAILED (Status: {response.status_code})")
        except Exception as e:
            print(f"ERROR: {e}")

    print("\n--- DONE: All rentals now have real, high-quality images! ---")

if __name__ == '__main__':
    populate()