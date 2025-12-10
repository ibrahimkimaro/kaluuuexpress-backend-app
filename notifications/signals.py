from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from shipping.models import Shipment
from .models import Notification
from .utils import send_push_notification


@receiver(pre_save, sender=Shipment)
def notify_shipment_changes(sender, instance, **kwargs):
    """Send notification when shipment status or route changes"""
    if not instance.pk or not instance.customer:
        return  # New shipment or no customer assigned
    
    try:
        old_instance = Shipment.objects.get(pk=instance.pk)
        
        # Notify on status change
        if old_instance.status != instance.status:
            title = f"Shipment Status Updated"
            message = f"Your shipment {instance.tracking_code} is now {instance.get_status_display()}"
            
            notification = Notification.objects.create(
                user=instance.customer,
                notification_type='shipment_status',
                title=title,
                message=message,
                data={
                    'shipment_id': instance.id,
                    'tracking_code': instance.tracking_code,
                    'status': instance.status,
                    'status_display': instance.get_status_display()
                }
            )
            
            # Send push notification
            send_push_notification(
                user=instance.customer,
                title=title,
                message=message,
                data=notification.data
            )
        
        # Notify on route stage change
        if old_instance.current_route_stage != instance.current_route_stage:
            title = f"📍 Shipment Location Updated"
            message = f"Your shipment {instance.tracking_code} has arrived at {instance.get_current_route_stage_display()}"
            
            notification = Notification.objects.create(
                user=instance.customer,
                notification_type='shipment_route',
                title=title,
                message=message,
                data={
                    'shipment_id': instance.id,
                    'tracking_code': instance.tracking_code,
                    'route_stage': instance.current_route_stage,
                    'route_stage_display': instance.get_current_route_stage_display(),
                    'progress': instance.route_progress
                }
            )
            
            # Send push notification
            send_push_notification(
                user=instance.customer,
                title=title,
                message=message,
                data=notification.data
            )
            
    except Shipment.DoesNotExist:
        pass
