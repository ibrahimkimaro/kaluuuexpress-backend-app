from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import (
    User, EmailVerification, PasswordResetToken, 
    LoginHistory, UserSession
)
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer,
    UserSerializer, UserProfileUpdateSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer, LoginHistorySerializer
)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def create_login_history(request, user, is_successful=True, failure_reason=None):
    """Create login history record"""
    LoginHistory.objects.create(
        user=user,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        is_successful=is_successful,
        failure_reason=failure_reason
    )


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
      
        # Create login history
        create_login_history(request, user, is_successful=True)
        
        return Response({
            'success': True,
            'message': 'Registration successful. Please verify your email.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer
    
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            # Update last login
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])
            
            # Create login history for security tracking
            create_login_history(request, user, is_successful=True)
            
            return Response({
                'success': True,
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log failed login attempt
            if 'email' in request.data:
                try:
                    user = User.objects.get(email=request.data['email'])
                    create_login_history(
                        request, user, 
                        is_successful=False, 
                        failure_reason=str(e)
                    )
                except User.DoesNotExist:
                    pass
            
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    POST /api/auth/logout/
    
    Request body:
    {
        "refresh_token": "your_refresh_token"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        try:
            # Get refresh token from request
            refresh_token = request.data.get('refresh_token')
            
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Update login history
            LoginHistory.objects.filter(
                user=request.user,
                logout_time__isnull=True
            ).update(logout_time=timezone.now())
            
            return Response({
                'success': True,
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile
    GET /api/auth/profile/ - Get user profile
    PUT/PATCH /api/auth/profile/ - Update user profile
    
    Update request body:
    {
        "full_name": " ",
        "phone_number": "+255123456789",
        "address": "123 Main St",
        "city": "Dar es Salaam",
        "country": "Tanzania",
        :profile_picture",
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get_object(self):
        return self.request.user
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserProfileUpdateSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully',
            'user': UserSerializer(instance).data
        })


class ChangePasswordView(APIView):
    """
    API endpoint for changing password
    POST /api/auth/change-password/
    
    Request body:
    {
        "old_password": "OldPass123",
        "new_password": "NewPass123",
        "confirm_password": "NewPass123"
    }
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.password_changed_at = timezone.now()
            user.save()
            
            return Response({
                'success': True,
                'message': 'Password changed successfully. Please login again.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """
    API endpoint for requesting password reset
    POST /api/auth/password-reset/

    Request body:
    {
        "email": "user@example.com"
    }
    """

    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = secrets.token_urlsafe(32)
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timedelta(hours=1),
                    ip_address=get_client_ip(request)
                )
                
                # TODO: Send password reset email
                # send_password_reset_email(user.email, token)
                
            except User.DoesNotExist:
                # Don't reveal whether user exists
                pass
            
            return Response({
                'success': True,
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    API endpoint for confirming password reset
    POST /api/auth/password-reset-confirm/

    Request body:
    {
        "token": "reset_token_here",
        "new_password": "NewPass123",
        "confirm_password": "NewPass123"
    }
    """
    authentication_classes = []  # Disable authentication (and CSRF) for password reset confirm
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token)
                
                if not reset_token.is_valid():
                    return Response({
                        'success': False,
                        'error': 'Invalid or expired reset token.'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Reset password
                user = reset_token.user
                user.set_password(new_password)
                user.password_changed_at = timezone.now()
                user.failed_login_attempts = 0
                user.account_locked_until = None
                user.save()
                
                # Mark token as used
                reset_token.is_used = True
                reset_token.save()
                
                return Response({
                    'success': True,
                    'message': 'Password reset successful. Please login with your new password.'
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Invalid reset token.'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    """
    API endpoint for email verification
    POST /api/auth/verify-email/

    Request body:
    {
        "token": "verification_token_here"
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        token = request.data.get('token')
        
        if not token:
            return Response({
                'success': False,
                'error': 'Token is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            verification = EmailVerification.objects.get(token=token)
            
            if not verification.is_valid():
                return Response({
                    'success': False,
                    'error': 'Invalid or expired verification token.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify user email
            user = verification.user
            user.is_verified = True
            user.save()
            
            # Mark token as used
            verification.is_used = True
            verification.save()
            
            return Response({
                'success': True,
                'message': 'Email verified successfully.'
            }, status=status.HTTP_200_OK)
            
        except EmailVerification.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Invalid verification token.'
            }, status=status.HTTP_400_BAD_REQUEST)


class LoginHistoryView(generics.ListAPIView):
    """
    API endpoint for viewing login history
    GET /api/auth/login-history/
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = LoginHistorySerializer
    
    def get_queryset(self):
        return LoginHistory.objects.filter(user=self.request.user).order_by('-login_time')
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'success': True,
            'login_history': serializer.data
        })


class ActiveDevicesView(APIView):
    """
    API endpoint for viewing active devices and terminating them
    GET /api/auth/devices/ - View all devices that have logged in
    DELETE /api/auth/devices/ - Terminate all other devices (logout everywhere)
    """
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Get recent login history to show active devices"""
        recent_logins = LoginHistory.objects.filter(
            user=request.user,
            is_successful=True
        ).order_by('-login_time')[:10]
        
        devices_data = [{
            'id': str(login.id),
            'ip_address': login.ip_address,
            'user_agent': login.user_agent,
            'login_time': login.login_time,
            'location': login.location,
        } for login in recent_logins]
        
        return Response({
            'success': True,
            'devices': devices_data,
            'total_count': len(devices_data)
        }, status=status.HTTP_200_OK)
    
    def delete(self, request):
        """Force logout on all other devices by invalidating all tokens"""
        # This will require the user to login again on all devices
        # In a real implementation, you would need a token versioning system
        
        return Response({
            'success': True,
            'message': 'Please change your password to logout from all other devices.'
        }, status=status.HTTP_200_OK)


class ResendVerificationEmailView(APIView):
    """
    API endpoint for resending verification email
    POST /api/auth/resend-verification/

    Request body:
    {
        "email": "user@example.com"
    }
    """
    authentication_classes = []  # Disable authentication (and CSRF) for resend verification
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'error': 'Email is required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            
            if user.is_verified:
                return Response({
                    'success': False,
                    'error': 'Email is already verified.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Invalidate old tokens
            EmailVerification.objects.filter(user=user).update(is_used=True)
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            EmailVerification.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            # TODO: Send verification email
            # send_verification_email(user.email, token)
            
            return Response({
                'success': True,
                'message': 'Verification email sent successfully.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'User with this email does not exist.'
            }, status=status.HTTP_404_NOT_FOUND)
