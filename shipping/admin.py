# shipping/admin.py

from django.contrib import admin
from django.urls import path
from django.http import JsonResponse
from django.utils.html import format_html
from django.db.models import Count, Sum
from .models import PackingList, ServiceTier, WeightHandling, Invoice, Shipment


# ============ Service Tier & Weight Handling Admin ============
@admin.register(ServiceTier)
class ServiceTierAdmin(admin.ModelAdmin):
    list_display = ("name", "price_per_kg_usd", "description")
    search_fields = ("name",)
    list_editable = ("price_per_kg_usd",)
    list_per_page = 20


@admin.register(WeightHandling)
class WeightHandlingAdmin(admin.ModelAdmin):
    list_display = ("name", "rate_tsh_per_kg", "description")
    search_fields = ("name",)
    list_editable = ("rate_tsh_per_kg",)
    list_per_page = 20


# ============ Invoice Admin ============
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        "invoice_number", 
        "user_name", 
        "description", 
        "quantity", 
        "weight_kg",
        "service_tier", 
        "total_amount_display",
        "credit_amount_display",
        "payment_status_badge", 
        "created_at"
    )
    search_fields = ("invoice_number", "user__email", "user__full_name", "description")
    list_filter = ("payment_status", "created_at", "service_tier", "weight_handling")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 25
    
    readonly_fields = ('invoice_number', 'total_amount', 'credit_amount', 'created_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('invoice_number', 'user', 'description', 'packages', 'quantity')
        }),
        ('Weight & Service', {
            'fields': ('weight_kg', 'service_tier', 'weight_handling')
        }),
        ('Billing Information', {
            'fields': ('total_amount', 'paying_bill', 'credit_amount', 'payment_status'),
            'description': 'Total amount is calculated from weight, service tier, and weight handling. Enter the paying bill amount, and credit amount will be calculated automatically.'
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    class Media:
        js = ('admin/js/invoice_calculator.js',)
    
    def user_name(self, obj):
        return obj.user.full_name if obj.user else 'N/A'
    user_name.short_description = 'Customer'
    user_name.admin_order_field = 'user__full_name'
    
    def total_amount_display(self, obj):
        formatted_amount = f'TSH {obj.total_amount:,.2f}'
        return format_html('<strong>{}</strong>', formatted_amount)
    total_amount_display.short_description = 'Total'
    total_amount_display.admin_order_field = 'total_amount'
    
    def credit_amount_display(self, obj):
        if obj.credit_amount > 0:
            formatted_credit = f'TSH {obj.credit_amount:,.2f}'
            return format_html('<span style="color: {};">{}</span>', '#dc3545', formatted_credit)
        return format_html('<span style="color: {};">{}</span>', '#28a745', 'TSH 0.00')
    credit_amount_display.short_description = 'Credit'
    credit_amount_display.admin_order_field = 'credit_amount'
    
    def payment_status_badge(self, obj):
        colors = {
            'paid': '#28a745',
            'unpaid': '#dc3545',
            'partially_paid': '#ffc107'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_status, '#6c757d'),
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Status'
    
    actions = ['mark_as_paid', 'mark_as_unpaid']
    
    def mark_as_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f'{updated} invoice(s) marked as paid.')
    mark_as_paid.short_description = 'Mark as Paid'
    
    def mark_as_unpaid(self, request, queryset):
        updated = queryset.update(payment_status='unpaid')
        self.message_user(request, f'{updated} invoice(s) marked as unpaid.')
    mark_as_unpaid.short_description = 'Mark as Unpaid'
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('get-prices/', self.admin_site.admin_view(self.get_prices), name='invoice_get_prices'),
        ]
        return custom_urls + urls
    
    def get_prices(self, request):
        """Return pricing data for service tier and weight handling"""
        service_tier_id = request.GET.get('service_tier_id')
        weight_handling_id = request.GET.get('weight_handling_id')
        
        data = {
            'service_price': 0,
            'handling_rate': 0,
        }
        
        try:
            if service_tier_id:
                service_tier = ServiceTier.objects.get(pk=service_tier_id)
                data['service_price'] = float(service_tier.price_per_kg_usd)
        except ServiceTier.DoesNotExist:
            pass
        
        try:
            if weight_handling_id:
                weight_handling = WeightHandling.objects.get(pk=weight_handling_id)
                data['handling_rate'] = float(weight_handling.rate_tsh_per_kg)
        except WeightHandling.DoesNotExist:
            pass
        
        return JsonResponse(data)


# ============ Shipment Admin ============
@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = (
        'tracking_code',
        'customer_display',
        'customer_email',
        'status_badge',
        'current_route_stage_badge',
        'route_progress_bar',
        'origin',
        'destination',
        'weight',
        'registered_date',
        'estimated_delivery'
    )
    list_filter = ('status', 'current_route_stage', 'registered_date', 'estimated_delivery')
    search_fields = (
        'tracking_code', 
        'customer__email', 
        'customer__full_name',
        'customer_name',
        'customer_email',
        'customer_phone'
    )
    readonly_fields = (
        'registered_date', 
        'last_updated', 
        'actual_delivery_date',
        'route_progress_display',
        'is_delivered'
    )
    date_hierarchy = 'registered_date'
    ordering = ('-registered_date',)
    list_per_page = 25
    
    fieldsets = (
        ('Tracking Information', {
            'fields': ('tracking_code', 'status', 'current_route_stage', 'route_progress_display', 'is_delivered')
        }),
        ('Customer Details', {
            'fields': ('customer', 'customer_name', 'customer_email', 'customer_phone')
        }),
        ('Shipment Details', {
            'fields': ('origin', 'destination', 'weight', 'description')
        }),
        ('Delivery Information', {
            'fields': ('registered_date', 'last_updated', 'estimated_delivery', 'actual_delivery_date')
        }),
        ('Admin Notes', {
            'fields': ('admin_notes',),
            'classes': ('collapse',)
        }),
    )
    
    def customer_display(self, obj):
        """Display customer name or 'N/A' if not set"""
        if obj.customer:
            return obj.customer.full_name
        return obj.customer_name or 'N/A'
    customer_display.short_description = 'Customer'
    
    def route_progress_display(self, obj):
        """Display route progress as percentage"""
        return f"{obj.route_progress:.0f}%"
    route_progress_display.short_description = 'Route Progress'
    
    def route_progress_bar(self, obj):
        """Display progress bar"""
        progress = obj.route_progress
        color = '#28a745' if progress == 100 else '#17a2b8' if progress > 50 else '#ffc107'
        progress_text = f'{progress:.0f}%'
        return format_html(
            '<div style="width:100px; background-color:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background-color:{}; height:20px; border-radius:3px; text-align:center; color:white; font-size:11px; line-height:20px;">{}</div>'
            '</div>',
            progress, color, progress_text
        )
    route_progress_bar.short_description = 'Progress'
    
    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'intransit': '#17a2b8',
            'delivered': '#28a745'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def current_route_stage_badge(self, obj):
        return format_html(
            '<span style="background-color: #6c757d; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            obj.get_current_route_stage_display()
        )
    current_route_stage_badge.short_description = 'Route Stage'
    
    actions = ['mark_intransit', 'mark_delivered', 'update_to_next_stage']
    
    def mark_intransit(self, request, queryset):
        updated = queryset.update(status='intransit')
        self.message_user(request, f'{updated} shipment(s) marked as in transit.')
    mark_intransit.short_description = 'Mark as In Transit'
    
    def mark_delivered(self, request, queryset):
        from django.utils import timezone
        for shipment in queryset:
            shipment.status = 'delivered'
            shipment.actual_delivery_date = timezone.now()
            shipment.save()
        self.message_user(request, f'{queryset.count()} shipment(s) marked as delivered.')
    mark_delivered.short_description = 'Mark as Delivered'
    
    def update_to_next_stage(self, request, queryset):
        """Move shipments to next route stage"""
        stage_order = ['china', 'ethiopia', 'zanzibar', 'dar_es_salaam']
        updated = 0
        for shipment in queryset:
            try:
                current_index = stage_order.index(shipment.current_route_stage)
                if current_index < len(stage_order) - 1:
                    shipment.current_route_stage = stage_order[current_index + 1]
                    shipment.save()
                    updated += 1
            except ValueError:
                continue
        self.message_user(request, f'{updated} shipment(s) moved to next stage.')
    update_to_next_stage.short_description = 'Move to Next Stage'




@admin.register(PackingList)
class PackingListAdmin(admin.ModelAdmin):
    list_display = ['code', 'date', 'created_by_name', 'total_cartons', 'total_weight', 'created_at']
    list_filter = ['date', 'created_by']
    search_fields = ['code', 'created_by__full_name', 'created_by__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'date', 'created_by')
        }),
        ('Packing Details', {
            'fields': ('total_cartons', 'total_weight', 'pdf_file')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else 'N/A'
    created_by_name.short_description = 'Created By'
    


    