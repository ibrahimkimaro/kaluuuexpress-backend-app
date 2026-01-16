import os
import django
import time
import logging
import threading

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend_app.settings')
django.setup()

from authentication.utils.email import EmailThread

# Setup basic logging to console
logging.basicConfig(level=logging.INFO)

def test_email_thread_ssl():
    print("Attempting to send email via EmailThread (SSL)...")
    
    subject = 'Test Thread SSL Email from Kaluu Express'
    html_content = '<p>This is a test email sent via a background thread using SSL.</p>'
    recipient_list = ['kaluuexpressaircargo@gmail.com']
    
    email_thread = EmailThread(subject, html_content, recipient_list)
    email_thread.start()
    
    print("Thread started. Waiting for completion...")
    email_thread.join()
    print("Thread finished.")

if __name__ == '__main__':
    test_email_thread_ssl()
