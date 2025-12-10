from rest_framework import serializers
from .models import ServiceTier, WeightHandling, Invoice, Shipment


# ============ Service Tier & Weight Handling Serializers ============
class ServiceTierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceTier
        fields = '__all__'


class WeightHandlingSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeightHandling
        fields = '__all__'


# ============ Invoice Serializers ============
class InvoiceSerializer(serializers.ModelSerializer):
    user_full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Invoice
        fields = '__all__'
        read_only_fields = ['invoice_number', 'total_amount', 'credit_amount', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user_full_name'] = instance.user.full_name
        return representation


# ============ Shipment Tracking Serializers ============
class ShipmentSerializer(serializers.ModelSerializer):
    """Complete shipment details"""
    customer_full_name = serializers.CharField(source='customer.full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    current_route_stage_display = serializers.CharField(source='get_current_route_stage_display', read_only=True)
    route_progress = serializers.ReadOnlyField()
    is_delivered = serializers.ReadOnlyField()
    
    class Meta:
        model = Shipment
        fields = [
            'id',
            'tracking_code',
            'customer',
            'customer_full_name',
            'customer_name',
            'customer_email',
            'customer_phone',
            'origin',
            'destination',
            'weight',
            'description',
            'status',
            'status_display',
            'current_route_stage',
            'current_route_stage_display',
            'route_progress',
            'is_delivered',
            'registered_date',
            'last_updated',
            'estimated_delivery',
            'actual_delivery_date',
            'admin_notes'
        ]
        read_only_fields = [
            'id',
            'registered_date',
            'last_updated',
            'route_progress',
            'is_delivered'
        ]


class ShipmentCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating shipments"""
    
    class Meta:
        model = Shipment
        fields = [
            'tracking_code',
            'customer',
            'customer_name',
            'customer_email',
            'customer_phone',
            'origin',
            'destination',
            'weight',
            'description',
            'estimated_delivery',
            'admin_notes'
        ]
