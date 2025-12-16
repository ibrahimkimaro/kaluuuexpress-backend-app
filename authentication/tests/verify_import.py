import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_app.settings')
django.setup()

from authentication.views import RequestPasswordResetView
print("Import successful")
