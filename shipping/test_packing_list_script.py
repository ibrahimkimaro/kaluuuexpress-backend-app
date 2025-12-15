import sys
import os
import django
from django.conf import settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

# Add project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# Configure minimal Django settings
if not settings.configured:
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'shipping',
            'authentication', # Assuming this is the app for custom user
        ],
        AUTH_USER_MODEL='authentication.User', # Adjust if needed
        TIME_ZONE='UTC',
        USE_TZ=True,
    )
    django.setup()

from shipping.models import PackingList
from django.contrib.auth import get_user_model

User = get_user_model()

def test_packing_list_creation():
    print("Testing PackingList creation...")
    
    # Create a dummy user
    user, created = User.objects.get_or_create(email='test@example.com', defaults={'username': 'testuser', 'full_name': 'Test User'})
    
    # Create a dummy PDF file
    pdf_file = SimpleUploadedFile("test.pdf", b"file_content", content_type="application/pdf")
    
    # Create first packing list
    pl1 = PackingList(created_by=user, pdf_file=pdf_file)
    pl1.save()
    print(f"Created PL1: {pl1.code}")
    
    # Create second packing list
    pl2 = PackingList(created_by=user, pdf_file=pdf_file)
    pl2.save()
    print(f"Created PL2: {pl2.code}")
    
    # Verify codes
    today_str = timezone.now().strftime('%Y%m%d')
    expected_code1 = f"PL-{today_str}-001"
    expected_code2 = f"PL-{today_str}-002"
    
    assert pl1.code == expected_code1, f"Expected {expected_code1}, got {pl1.code}"
    assert pl2.code == expected_code2, f"Expected {expected_code2}, got {pl2.code}"
    
    print("SUCCESS: PackingList codes generated correctly!")

if __name__ == "__main__":
    try:
        test_packing_list_creation()
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
