import firebase_admin
from firebase_admin import credentials, messaging
from django.conf import settings
from .models import UserDevice
import logging

logger = logging.getLogger(__name__)


def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    if not firebase_admin._apps:
        try:
            # You'll need to download your Firebase service account key
            # and place it in your project
            cred_path = getattr(settings, 'FIREBASE_CREDENTIALS_PATH', None)
            if cred_path:
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                logger.warning("Firebase credentials path not set in settings")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")


def send_push_notification(user, title, message, data=None):
    """
    Send push notification to all user's devices
    
    Args:
        user: User object
        title: Notification title
        message: Notification message
        data: Dict of additional data
    """
    try:
        initialize_firebase()
        
        # Get all active devices for the user
        devices = UserDevice.objects.filter(user=user, is_active=True)
        
        if not devices.exists():
            logger.info(f"No active devices found for user {user.id}")
            return
        
        # Prepare notification data
        notification_data = data or {}
        notification_data['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
        
        success_count = 0
        failed_tokens = []
        
        for device in devices:
            try:
                # Create message
                fcm_message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=message,
                    ),
                    data={k: str(v) for k, v in notification_data.items()},  # FCM requires string values
                    token=device.device_token,
                    android=messaging.AndroidConfig(
                        priority='high',
                        notification=messaging.AndroidNotification(
                            sound='default',
                            color='#3b7ddd',  # Primary color
                        ),
                    ),
                    apns=messaging.APNSConfig(
                        payload=messaging.APNSPayload(
                            aps=messaging.Aps(
                                sound='default',
                                badge=1,
                            ),
                        ),
                    ),
                )
                
                # Send message
                response = messaging.send(fcm_message)
                logger.info(f"Successfully sent notification to {device.device_token[:20]}...")
                success_count += 1
                
            except messaging.UnregisteredError:
                # Token is no longer valid, mark device as inactive
                logger.warning(f"Device token {device.device_token[:20]}... is unregistered")
                device.is_active = False
                device.save()
                failed_tokens.append(device.device_token)
                
            except Exception as e:
                logger.error(f"Failed to send notification to {device.device_token[:20]}...: {e}")
                failed_tokens.append(device.device_token)
        
        logger.info(f"Sent {success_count}/{devices.count()} notifications successfully")
        
    except Exception as e:
        logger.error(f"Error in send_push_notification: {e}")


def send_bulk_notification(users, title, message, data=None):
    """Send notification to multiple users"""
    for user in users:
        send_push_notification(user, title, message, data)
