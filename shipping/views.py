from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import generics, permissions, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import viewsets, status, permissions
from django.shortcuts import get_object_or_404
from django.http import FileResponse
from rest_framework.decorators import action

from .models import ServiceTier, WeightHandling, Invoice, Shipment, PackingList
from .serializers import (
    ServiceTierSerializer, 
    WeightHandlingSerializer, 
    InvoiceSerializer,
    ShipmentSerializer,
    ShipmentCreateSerializer,
    PackingListSerializer
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




# Additional views for PackingList can be added similarly

class IsStaffOrPackingListCreatorOrReadOnly(permissions.BasePermission):
    """
    Custom permission:
    - Superusers can do anything
    - Staff users can edit/delete (but create only if they have permission)
    - Users with can_create_packing_list permission can create
    - Regular users can only read
    """
    def has_permission(self, request, view):
        # Read permissions for everyone
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated


        # Superuser can do anything
        if request.user.is_superuser:
            return True

        # Creation requires specific permission
        if request.method == 'POST':
            return getattr(request.user, 'can_create_packing_list', False)

        # Update/Delete requires staff
        return request.user.is_staff


        if request.method == 'POST' and getattr(request.user, 'can_create_packing_list', False):
            return True
        return False
        # Write permissions only for staff
        #return request.user and request.user.is_authenticated and request.user.is_staff


class PackingListViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Packing Lists
    
    GET /api/shipping/packing-lists/ - List all packing lists
    POST /api/shipping/packing-lists/ - Create new packing list (staff only)
    GET /api/shipping/packing-lists/{id}/ - Get specific packing list
    DELETE /api/shipping/packing-lists/{id}/ - Delete packing list (staff only)
    GET /api/shipping/packing-lists/{id}/download/ - Download PDF
    """
    
    queryset = PackingList.objects.all()
    serializer_class = PackingListSerializer
    permission_classes = [IsStaffOrPackingListCreatorOrReadOnly]
    
    def create(self, request, *args, **kwargs):
        """
        Create packing list with PDF upload
        Expects multipart/form-data with:
        - date: date string (YYYY-MM-DD)
        - total_cartons: integer
        - total_weight: decimal
        - pdf_file: PDF file
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set the creator
        serializer.save(created_by=request.user)
        
        headers = self.get_success_headers(serializer.data)
        return Response({
            'success': True,
            'message': 'Packing list created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download PDF file
        """
        packing_list = self.get_object()
        
        if not packing_list.pdf_file:
            return Response({
                'error': 'PDF file not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        try:
            return FileResponse(
                packing_list.pdf_file.open('rb'),
                as_attachment=True,
                filename=f'packing_list_{packing_list.unique_id}.pdf',
                content_type='application/pdf'
            )
        except Exception as e:
            return Response({
                'error': f'Failed to download PDF: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """Delete packing list"""
        instance = self.get_object()
        
        # Delete the PDF file from storage
        if instance.pdf_file:
            instance.pdf_file.delete(save=False)
        
        self.perform_destroy(instance)
        
        return Response({
            'success': True,
            'message': 'Packing list deleted successfully'
        }, status=status.HTTP_200_OK)
