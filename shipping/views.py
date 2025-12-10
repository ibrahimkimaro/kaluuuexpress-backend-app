from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ServiceTier, WeightHandling, Invoice, Shipment
from .serializers import (
    ServiceTierSerializer, 
    WeightHandlingSerializer, 
    InvoiceSerializer,
    ShipmentSerializer,
    ShipmentCreateSerializer
)


# ============ Shipping Configuration ============
@api_view(['GET'])
@permission_classes([AllowAny])
def get_shipping_config(request):
    """Get service tiers and weight handling options"""
    tiers = ServiceTier.objects.all()
    handling = WeightHandling.objects.all()

    return Response({
        "service_tiers": ServiceTierSerializer(tiers, many=True).data,
        "weight_handling": WeightHandlingSerializer(handling, many=True).data
    })


# ============ Invoice Views ============
class InvoiceListCreateView(generics.ListCreateAPIView):
    """List all invoices for the authenticated user, or create a new invoice"""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            # Admin can create invoice for any user
            serializer.save()
        else:
            # Regular user creates invoice for themselves
            serializer.save(user=self.request.user)


class InvoiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific invoice"""
    serializer_class = InvoiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Invoice.objects.all()
        return Invoice.objects.filter(user=self.request.user)


# ============ Shipment Views ============
class ShipmentListCreateView(generics.ListCreateAPIView):
    """List all shipments for the authenticated user, or create a new shipment"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            # Admin can see all shipments
            return Shipment.objects.all()
        # Regular users see only their shipments
        return Shipment.objects.filter(customer=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ShipmentCreateSerializer
        return ShipmentSerializer

    def perform_create(self, serializer):
        if self.request.user.is_staff:
            # Admin can create shipment for any customer
            serializer.save()
        else:
            # Regular user creates shipment for themselves
            serializer.save(customer=self.request.user)


class ShipmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a specific shipment by ID or tracking code"""
    serializer_class = ShipmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        if self.request.user.is_staff:
            return Shipment.objects.all()
        return Shipment.objects.filter(customer=self.request.user)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_shipment_by_tracking(request, tracking_code):
    """Retrieve a specific shipment by tracking code"""
    if request.user.is_staff:
        shipment = get_object_or_404(Shipment, tracking_code=tracking_code)
    else:
        shipment = get_object_or_404(
            Shipment,
            tracking_code=tracking_code,
            customer=request.user
        )
    
    serializer = ShipmentSerializer(shipment)
    return Response(serializer.data)