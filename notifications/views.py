from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import UserDevice, Notification
from .serializers import UserDeviceSerializer, NotificationSerializer


class RegisterDeviceView(generics.CreateAPIView):
    """Register or update user's device token for push notifications"""
    serializer_class = UserDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        device_token = request.data.get('device_token')
        device_type = request.data.get('device_type', 'android')
        
        if not device_token:
            return Response(
                {'error': 'device_token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update or create device
        device, created = UserDevice.objects.update_or_create(
            user=request.user,
            device_token=device_token,
            defaults={'device_type': device_type, 'is_active': True}
        )
        
        serializer = self.get_serializer(device)
        return Response(
            {
                'message': 'Device registered successfully',
                'device': serializer.data
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


class NotificationListView(generics.ListAPIView):
    """Get all notifications for the authenticated user"""
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.objects.get(id=notification_id, user=request.user)
        notification.mark_as_read()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_notifications_read(request):
    """Mark all notifications as read for the authenticated user"""
    updated = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response({'message': f'{updated} notification(s) marked as read'})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """Get count of unread notifications"""
    count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': count})
