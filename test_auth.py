import requests
import json

BASE_URL = "http://localhost:8000/api"

def run_test():
    # 1. Register a new user
    email = "test_auth_user@example.com"
    password = "TestPassword123!"
    
    print(f"Registering user {email}...")
    register_data = {
        "email": email,
        "full_name": "Test Auth User",
        "phone_number": "+255712345678",
        "password": password,
        "confirm_password": password
    }
    
    # Try to register, if fails (already exists), try login
    resp = requests.post(f"{BASE_URL}/auth/register/", json=register_data)
    
    if resp.status_code == 201:
        print("Registration successful.")
        tokens = resp.json()['tokens']
    else:
        print(f"Registration failed ({resp.status_code}). Trying login...")
        login_data = {"email": email, "password": password}
        resp = requests.post(f"{BASE_URL}/auth/login/", json=login_data)
        if resp.status_code == 200:
            print("Login successful.")
            tokens = resp.json()['tokens']
        else:
            print(f"Login failed: {resp.text}")
            return

    access_token = tokens['access']
    print(f"Got access token: {access_token[:10]}...")

    # 2. Try to access invoices
    print("Accessing /shipping/invoices/ with token...")
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get(f"{BASE_URL}/shipping/invoices/", headers=headers)
    
    print(f"Response Status: {resp.status_code}")
    print(f"Response Body: {resp.text}")

if __name__ == "__main__":
    run_test()
