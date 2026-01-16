import os
import django
from django.core.mail import send_mail
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_app.settings')
django.setup()

def test_email_send_ssl():
    print(f"Attempting to send email using current settings...")
    print(f"Host: {settings.EMAIL_HOST}")
    print(f"Port: {settings.EMAIL_PORT}")
    print(f"User: {settings.EMAIL_HOST_USER}")
    print(f"Use SSL: {settings.EMAIL_USE_SSL}")
    
    try:
        send_mail(
            subject='Test SSL Email from Kaluu Express',
            message='This is a test email sent via SSL to verify configuration.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['kaluuexpressaircargo@gmail.com'], 
            fail_silently=False,
        )
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == '__main__':
    test_email_send_ssl()
