from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    ChangePasswordView,
    RequestPasswordResetView,
    PasswordResetConfirmView,
    EmailVerificationView,
    LoginHistoryView,
    ActiveDevicesView,
    ResendVerificationEmailView,
)

app_name = 'authentication'
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # ==================== Authentication Endpoints ====================
    
    # Registration & Login
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', csrf_exempt(UserLoginView.as_view()), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    
    # ==================== JWT Token Management ====================
    
    # Refresh access token
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # ==================== Profile Management ====================
    
    # Get and update user profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    
    # ==================== Password Management ====================
    
    # Change password (requires authentication)
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Request password reset (public)
    path('password-reset/', RequestPasswordResetView.as_view(), name='password_reset'),
    
    # Confirm password reset with token (public)
    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    
    # ==================== Email Verification ====================
    
    # Verify email with token (public)
    path('verify-email/', EmailVerificationView.as_view(), name='verify_email'),
    
    # Resend verification email (public)
    path('resend-verification/', ResendVerificationEmailView.as_view(), name='resend_verification'),
    
    path('login-history/', LoginHistoryView.as_view(), name='login_history'),
    
    # View and manage active devices (requires authentication)
    path('devices/', ActiveDevicesView.as_view(), name='active_devices'),
]


"""
API ENDPOINTS DOCUMENTATION
===========================

PUBLIC ENDPOINTS (No authentication required):
----------------------------------------------

1. POST /api/auth/register/
   - Register new user
   - Body: { email, full_name, phone_number, password, confirm_password }
   - Returns: { success, message, user, tokens }

2. POST /api/auth/login/
   - Login user
   - Body: { email, password }
   - Returns: { success, message, user, tokens, session_key }

3. POST /api/auth/password-reset/
   - Request password reset
   - Body: { email }
   - Returns: { success, message }

4. POST /api/auth/password-reset-confirm/
   - Confirm password reset with token
   - Body: { token, new_password, confirm_password }
   - Returns: { success, message }

5. POST /api/auth/verify-email/
   - Verify email with token
   - Body: { token }
   - Returns: { success, message }

6. POST /api/auth/resend-verification/
   - Resend verification email
   - Body: { email }
   - Returns: { success, message }

7. POST /api/auth/token/refresh/
   - Refresh access token
   - Body: { refresh }
   - Returns: { access }


AUTHENTICATED ENDPOINTS (Requires JWT token):
---------------------------------------------

8. POST /api/auth/logout/
   - Logout user
   - Headers: Authorization: Bearer <access_token>
   - Body: { refresh_token, session_key }
   - Returns: { success, message }

9. GET /api/auth/profile/
   - Get user profile
   - Headers: Authorization: Bearer <access_token>
   - Returns: { success, user }

10. PUT/PATCH /api/auth/profile/
    - Update user profile
    - Headers: Authorization: Bearer <access_token>
    - Body: { full_name, phone_number, address, city, country, postal_code }
    - Returns: { success, message, user }

11. POST /api/auth/change-password/
    - Change password
    - Headers: Authorization: Bearer <access_token>
    - Body: { old_password, new_password, confirm_password }
    - Returns: { success, message }

12. GET /api/auth/login-history/
    - View login history
    - Headers: Authorization: Bearer <access_token>
    - Returns: { success, login_history }

13. GET /api/auth/devices/
    - View recent login devices
    - Headers: Authorization: Bearer <access_token>
    - Returns: { success, devices, total_count }

14. DELETE /api/auth/devices/
    - Force logout on all other devices
    - Headers: Authorization: Bearer <access_token>
    - Returns: { success, message }


USAGE EXAMPLES:
--------------

# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone_number": "+255123456789",
    "password": "SecurePass123",
    "confirm_password": "SecurePass123"
  }'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'

# Get Profile (with token)
curl -X GET http://localhost:8000/api/auth/profile/ \
  -H "Authorization: Bearer <your_access_token>"

# Change Password
curl -X POST http://localhost:8000/api/auth/change-password/ \
  -H "Authorization: Bearer <your_access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "SecurePass123",
    "new_password": "NewPass456",
    "confirm_password": "NewPass456"
  }'
"""
