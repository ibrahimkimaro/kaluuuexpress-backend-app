from django.core.mail import send_mail
from django.conf import settings
import threading
class EmailThread(threading.Thread):
    def __init__(self, subject, html_content, recipient_list):
        self.subject = subject
        self.recipient_list = recipient_list
        self.html_content = html_content
        threading.Thread.__init__(self)
    def run(self):
        send_mail(
            subject=self.subject,
            message='',  # Plain text message (optional fallback)
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=self.recipient_list,
            html_message=self.html_content,
            fail_silently=False,
        )
def send_password_reset_email(email, reset_link):
    """
    Sends a password reset email to the user.
    """
    subject = "Password Reset Request - Kaluu Express Cargo"
    
    html_content = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #4A90E2;">Password Reset Request</h2>
        <p>Hello,</p>
        <p>We received a request to reset your password for your Kaluu Express Cargo account.</p>
        <p>Click the button below to reset your password:</p>
        <a href="{reset_link}" style="display: inline-block; padding: 12px 24px; background-color: #4A90E2; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
        <p style="margin-top: 20px;">If you didn't request this, you can safely ignore this email.</p>
        <p>Best regards,<br>Kaluu Express Cargo Team</p>
    </div>
    """
    # Send email in a separate thread to avoid blocking the request
    EmailThread(subject, html_content, [email]).start()