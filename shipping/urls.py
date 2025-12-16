# shipping/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'packing-lists', views.PackingListViewSet, basename='packing-list')

urlpatterns = [
    # Shipping Configuration
    path("config/", views.get_shipping_config, name="shipping-config"),
    
    # Invoice Endpoints
    path('invoices/', views.InvoiceListCreateView.as_view(), name='invoice-list-create'),
    path('invoices/<uuid:pk>/', views.InvoiceDetailView.as_view(), name='invoice-detail'),
    
    # Shipment Endpoints
    path('shipments/', views.ShipmentListCreateView.as_view(), name='shipment-list-create'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment-detail'),
    path('shipments/track/<str:tracking_code>/', views.get_shipment_by_tracking, name='shipment-by-tracking'),

    # Packing List Endpoints (via Router)
    path('', include(router.urls)),
]
