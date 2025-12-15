# utils/email.py
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

def send_password_reset_email(email: str, token: str):
    reset_link = f"http://157.245.227.236/api/auth/reset-password?token={token}"
    
    subject = "Kaluu Express Cargo Password Reset"
    message = f"""
    Hi,

    You requested a password reset. Click the link below to reset your password:

    {reset_link}

    This link will expire in 1 hour.

    If you did not request this, you can safely ignore this email.
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
