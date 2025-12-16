from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User
from django import forms
from django.utils.html import format_html


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['-date_joined']
    list_display = ['id', 'full_name', 'email', 'phone_number', 'country', 'city', 'is_active', 'is_staff', 'user_status']
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'country', 'date_joined')
    search_fields = ('phone_number', 'email', 'full_name', 'country', 'city')
    list_per_page = 25
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        ('Authentication', {
            'fields': ('phone_number', 'password')
        }),
        ('Personal Information', {
            'fields': ('full_name', 'email', 'profile_picture', 'country', 'city')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'can_create_packing_list'),
            'classes': ('collapse',)
        }),
        ('Advanced Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('full_name', 'email', 'phone_number', 'country', 'city', 'profile_picture', 'password1', 'password2'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def user_status(self, obj):
        """Display colored status badge"""
        if obj.is_superuser:
            return format_html('<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>', '#dc3545', 'Superuser')
        elif obj.is_staff:
            return format_html('<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>', '#17a2b8', 'Staff')
        elif obj.is_active:
            return format_html('<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>', '#28a745', 'Active')
        else:
            return format_html('<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>', '#6c757d', 'Inactive')
    
    user_status.short_description = 'Status'
    
    actions = ['activate_users', 'deactivate_users', 'make_staff']
    
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} user(s) promoted to staff.')
    make_staff.short_description = 'Promote to staff'