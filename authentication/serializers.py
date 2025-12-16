from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .models import LoginHistory
import re

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'},min_length=6)
    confirm_password = serializers.CharField(write_only=True,required=True,style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = [
            'email', 'full_name', 'phone_number',
            'country','city',
            'password', 'confirm_password'
        ]
        extra_kwargs = {
            'email': {'required': True},
            'full_name': {'required': True},
            'phone_number': {'required': True},
             'country':{'required':True},
            'city':{'required':True}, 
        }
    
    def validate_full_name(self, value):
        """Validate full name"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        
        # Check if name contains at least one letter
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError("Full name must contain at least one letter.")
        
        return value.strip()

    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        # Additional password validation
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        
        # Check for at least one letter and one number
        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError("Password must contain at least one letter.")
        
        if not re.search(r'\d', value):
            raise serializers.ValidationError("Password must contain at least one number.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create and return a new user"""
        validated_data.pop('confirm_password')
        
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data['full_name'],
            phone_number=validated_data['phone_number'],
            country=validated_data.get('country', ''),  # ← ADD THIS
            city=validated_data.get('city', ''),
        )
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Normalize email"""
        return value.lower()
    
    def validate(self, attrs):
        """Validate user credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Check if user exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'non_field_errors': 'Invalid email or password.'
                })
            
            # Check if account is locked
            if user.is_account_locked():
                raise serializers.ValidationError({
                    'non_field_errors': 'Account is temporarily locked due to multiple failed login attempts. Please try again later.'
                })
            
            # Check if account is active
            if not user.is_active:
                raise serializers.ValidationError({
                    'non_field_errors': 'This account has been deactivated.'
                })
            
            # Authenticate user
            user = authenticate(
                request=self.context.get('request'),
                email=email,
                password=password
            )
            
            if not user:
                # Increment failed login attempts
                try:
                    user_obj = User.objects.get(email=email)
                    user_obj.failed_login_attempts += 1
                    
                    # Lock account after 5 failed attempts
                    if user_obj.failed_login_attempts >= 5:
                        from django.utils import timezone
                        from datetime import timedelta
                        user_obj.account_locked_until = timezone.now() + timedelta(minutes=2)
                    
                    user_obj.save()
                except User.DoesNotExist:
                    pass
                
                raise serializers.ValidationError({
                    'non_field_errors': 'Invalid email or password.'
                })
            
            # Reset failed login attempts on successful login
            user.failed_login_attempts = 0
            user.account_locked_until = None
            user.save()
            
            attrs['user'] = user
        else:
            raise serializers.ValidationError({
                'non_field_errors': 'Must include "email" and "password".'
            })
        
        return attrs


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'full_name', 'phone_number',
            'profile_picture', 'city', 'country',
         'is_verified', 'date_joined', 'can_create_packing_list'
        ]
        read_only_fields = ['id', 'email', 'is_verified', 'date_joined', 'can_create_packing_list']


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = User
        fields = [
            'full_name', 'phone_number', 'profile_picture',
             'city', 'country', 
        ]
    
    def validate_full_name(self, value):
        """Validate full name"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Full name must be at least 3 characters long.")
        return value.strip()


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_old_password(self, value):
        """Validate old password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        
        return value
    
    def validate(self, attrs):
        """Validate that new passwords match"""
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        
        # Ensure new password is different from old password
        if attrs.get('old_password') == attrs.get('new_password'):
            raise serializers.ValidationError({
                'new_password': "New password must be different from old password."
            })
        
        return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that user with this email exists"""
        try:
            user = User.objects.get(email__iexact=value)
            if not user.is_active:
                raise serializers.ValidationError("This account is not active.")
        except User.DoesNotExist:
            # Don't reveal whether user exists for security
            pass
        
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset"""
    
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    confirm_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate password strength"""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long.")
        
        return value
    
    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs.get('new_password') != attrs.get('confirm_password'):
            raise serializers.ValidationError({
                'confirm_password': "Passwords do not match."
            })
        return attrs


class LoginHistorySerializer(serializers.ModelSerializer):
    """Serializer for login history"""
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'ip_address', 'user_agent', 'login_time',
            'logout_time', 'is_successful', 'failure_reason',
            'device_info', 'location'
        ]
        read_only_fields = fields
