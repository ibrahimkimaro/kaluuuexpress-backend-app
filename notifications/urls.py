from django.urls import path
from . import views

urlpatterns = [
    # Device registration
    path('register-device/', views.RegisterDeviceView.as_view(), name='register-device'),
    
    # Notifications
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:notification_id>/mark-read/', views.mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', views.mark_all_notifications_read, name='mark-all-notifications-read'),
    path('unread-count/', views.unread_count, name='unread-count'),
]
