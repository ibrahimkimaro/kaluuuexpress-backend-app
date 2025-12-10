from django.db import models
from django.conf import settings
from django.utils import timezone


class UserDevice(models.Model):
    """Store user device tokens for push notifications"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='devices')
    device_token = models.CharField(max_length=255, unique=True)
    device_type = models.CharField(max_length=20, choices=[('android', 'Android'), ('ios', 'iOS')], default='android')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Device'
        verbose_name_plural = 'User Devices'
        unique_together = ('user', 'device_token')
    
    def __str__(self):
        return f"{self.user.full_name} - {self.device_type}"


class Notification(models.Model):
    """Track sent notifications"""
    NOTIFICATION_TYPES = [
        ('shipment_status', 'Shipment Status Update'),
        ('shipment_route', 'Shipment Route Update'),
        ('invoice_payment', 'Invoice Payment Update'),
        ('general', 'General Notification'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    data = models.JSONField(null=True, blank=True)  # Extra data like shipment_id, tracking_code
    is_read = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.user.full_name} - {self.title}"
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
