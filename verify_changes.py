import os
import django
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from shipping.models import PackingList

User = get_user_model()

def verify_changes():
    print("Verifying changes...")
    
    # 1. Verify User Permission
    email = f"test_perm_{uuid.uuid4()}@example.com"
    password = "TestPassword123!"
    
    print(f"Creating user {email}...")
    user = User.objects.create_user(
        email=email,
        password=password,
        full_name="Test Permission User",
        phone_number="+255700000000"
    )
    
    print(f"Checking default permission: {user.can_create_packing_list}")
    if user.can_create_packing_list:
        print("FAIL: Default permission should be False")
    else:
        print("PASS: Default permission is False")
        
    print("Updating permission to True...")
    user.can_create_packing_list = True
    user.save()
    
    user.refresh_from_db()
    print(f"Checking updated permission: {user.can_create_packing_list}")
    if user.can_create_packing_list:
        print("PASS: Permission updated successfully")
    else:
        print("FAIL: Permission update failed")
        
    # 2. Verify Packing List Unique ID
    print("\nVerifying Packing List Unique ID...")
    code = f"TEST-{uuid.uuid4().hex[:6]}"
    
    print(f"Creating Packing List with code {code}...")
    packing_list = PackingList.objects.create(
        code=code,
        created_by=user,
        total_cartons=10,
        total_weight=100.50
    )
    
    print(f"Checking unique_id: {packing_list.unique_id}")
    if packing_list.unique_id and isinstance(packing_list.unique_id, uuid.UUID):
        print("PASS: unique_id is a valid UUID")
    else:
        print("FAIL: unique_id is missing or invalid")
        
    # Cleanup
    print("\nCleaning up...")
    packing_list.delete()
    user.delete()
    print("Done.")

if __name__ == "__main__":
    verify_changes()
