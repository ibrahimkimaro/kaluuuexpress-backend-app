import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_app.settings')
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from shipping.models import Invoice

User = get_user_model()

def test_regular_user_isolation():
    print("--- Setting up test data ---")
    # 1. Create a regular user
    user1_email = "regular_user_1@example.com"
    user1, created = User.objects.get_or_create(email=user1_email, defaults={
        "full_name": "Regular User 1",
        "phone_number": "+255700000001",
        "is_staff": False
    })
    if created:
        user1.set_password("password123")
        user1.save()
    print(f"User 1 created: {user1.email} (Staff: {user1.is_staff})")

    # 2. Create another user
    user2_email = "regular_user_2@example.com"
    user2, created = User.objects.get_or_create(email=user2_email, defaults={
        "full_name": "Regular User 2",
        "phone_number": "+255700000002",
        "is_staff": False
    })
    if created:
        user2.set_password("password123")
        user2.save()
    print(f"User 2 created: {user2.email}")

    # 3. Create invoices
    # Invoice for User 1
    inv1 = Invoice.objects.create(
        user=user1,
        description="User 1 Invoice",
        packages="Box",
        quantity=1,
        weight_kg=10,
        price_per_kg=100
    )
    print(f"Invoice created for User 1: {inv1.invoice_number}")

    # Invoice for User 2
    inv2 = Invoice.objects.create(
        user=user2,
        description="User 2 Invoice",
        packages="Bag",
        quantity=1,
        weight_kg=5,
        price_per_kg=100
    )
    print(f"Invoice created for User 2: {inv2.invoice_number}")

    print("\n--- Testing Access ---")
    
    # 4. Login as User 1 and fetch invoices
    client = APIClient()
    client.force_authenticate(user=user1)
    
    response = client.get('/api/shipping/invoices/')
    
    print(f"User 1 fetched invoices. Status: {response.status_code}")
    data = response.json()
    print(f"Count: {len(data)}")
    
    found_ids = [item['id'] for item in data]
    
    if str(inv1.id) in found_ids and str(inv2.id) not in found_ids:
        print("SUCCESS: User 1 sees their invoice and NOT User 2's invoice.")
    else:
        print("FAILURE: Visibility check failed.")
        print(f"Visible IDs: {found_ids}")
        print(f"User 1 Invoice ID: {inv1.id}")
        print(f"User 2 Invoice ID: {inv2.id}")

if __name__ == "__main__":
    test_regular_user_isolation()
