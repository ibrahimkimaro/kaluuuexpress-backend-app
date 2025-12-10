from rest_framework import serializers
from .models import UserDevice, Notification


class UserDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDevice
        fields = ['id', 'device_token', 'device_type', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'notification_type',
            'title',
            'message',
            'data',
            'is_read',
            'sent_at',
            'read_at'
        ]
        read_only_fields = ['id', 'sent_at', 'read_at']
