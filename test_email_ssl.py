import smtplib
import socket

def test_ssl_connection():
    host = 'smtp.gmail.com'
    port = 465
    timeout = 10
    
    print(f"Testing connection to {host}:{port}...")
    try:
        # Try to connect using SMTP_SSL
        server = smtplib.SMTP_SSL(host, port, timeout=timeout)
        print("Successfully connected to SMTP server over SSL!")
        server.quit()
    except socket.timeout:
        print("Connection timed out. Port likely blocked.")
    except OSError as e:
        print(f"Connection failed: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    test_ssl_connection()
