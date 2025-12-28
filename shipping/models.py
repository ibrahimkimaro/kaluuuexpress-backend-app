from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid
from decimal import Decimal


class ServiceTier(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_per_kg_usd = models.FloatField()  # Admin sets this

    def __str__(self):
        return self.name


class WeightHandling(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    rate_tsh_per_kg = models.FloatField()  # Admin sets this

    def __str__(self):
        return self.name



class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    invoice_number = models.CharField(max_length=50, unique=True, blank=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    description = models.CharField(max_length=255)
    packages = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2)

    service_tier = models.ForeignKey(
        "ServiceTier",
        on_delete=models.SET_NULL,
        null=True
    )

    weight_handling = models.ForeignKey(
        "WeightHandling",
        on_delete=models.SET_NULL,
        null=True
    )

    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paying_bill = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Total Paid")
    credit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    payment_status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("unpaid", "Unpaid"),
            ("partially_paid", "Partially Paid"),
        ],
        default="unpaid"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def update_payment_totals(self):
        """Recalculate total paid and credit amount based on related payments"""
        total_paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        self.paying_bill = total_paid
        self.credit_amount = self.total_amount - self.paying_bill
        
        # Update payment status
        if self.paying_bill >= self.total_amount:
            self.payment_status = 'paid'
        elif self.paying_bill > 0:
            self.payment_status = 'partially_paid'
        else:
            self.payment_status = 'unpaid'
            
        self.save()

    def save(self, *args, **kwargs):

        if not self.invoice_number:
            last = Invoice.objects.order_by("-created_at").first()
            if last:
                number = int(last.invoice_number.split("-")[1]) + 1
            else:
                number = 1
            self.invoice_number = f"INV-{number:04d}"

        # CALCULATION — backend only
        if self.service_tier and self.weight_handling:
            service_price = Decimal(self.service_tier.price_per_kg_usd)
            handling_price = Decimal(self.weight_handling.rate_tsh_per_kg)
            self.total_amount = self.weight_kg * service_price * handling_price
        
        # If this is an existing instance, we might want to ensure totals are correct
        # But usually update_payment_totals is called when payments change
        self.credit_amount = self.total_amount - Decimal(self.paying_bill)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number


class Payment(models.Model):
    """Model to track partial payments for an invoice"""
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank', 'Bank Transfer'),
        ('mobile', 'Mobile Money'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    reference_number = models.CharField(max_length=100, blank=True, null=True, help_text="Transaction ID or Receipt Number")
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
    
    def __str__(self):
        return f"{self.invoice.invoice_number} - {self.amount}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update invoice totals after saving payment
        self.invoice.update_payment_totals()
    
    def delete(self, *args, **kwargs):
        invoice = self.invoice
        super().delete(*args, **kwargs)
        # Update invoice totals after deleting payment
        invoice.update_payment_totals()




class Shipment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('intransit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]
    
    ROUTE_STAGES = [
        ('china', 'China'),
        ('ethiopia', 'Ethiopia'),
        ('zanzibar', 'Zanzibar'),
        ('dar_es_salaam', 'Dar es Salaam'),
    ]
    
    # Primary Information
    tracking_code = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipments')
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_email = models.EmailField(blank=True)
    customer_phone = models.CharField(max_length=20,null=True,blank=True)
    
    # Shipment Details
    origin = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    weight = models.DecimalField(max_digits=10, decimal_places=2, help_text="Weight in kg")
    description = models.TextField(blank=True, null=True)
    
    # Tracking Information
    status = models.CharField(choices=STATUS_CHOICES, max_length=20, default='pending')
    current_route_stage = models.CharField(choices=ROUTE_STAGES, max_length=20, default='china')
    
    # Timestamps
    registered_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    estimated_delivery = models.DateField(blank=True, null=True)
    actual_delivery_date = models.DateTimeField(blank=True, null=True)
    
    # Admin Notes
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-registered_date']
        verbose_name = 'Shipment'
        verbose_name_plural = 'Shipments'
    
    def __str__(self):
        return f"{self.tracking_code} - {self.status}"
    
    # def save(self, *args, **kwargs):
    #     # Generate unique tracking code
    #     if not self.tracking_code:
    #         self.tracking_code = self.generate_tracking_code()
    #     super().save(*args, **kwargs)
    
    # @staticmethod
    # def generate_tracking_code():
    #     """Generate unique tracking code like TRK-001234"""
    #     import random
    #     import string
    #     while True:
    #         code = f"TRK-{''.join(random.choices(string.digits, k=6))}"
    #         if not Shipment.objects.filter(tracking_code=code).exists():
    #             return code
    
    @property
    def route_progress(self):
        """Calculate progress percentage based on current route stage"""
        stages = ['china', 'ethiopia', 'zanzibar', 'dar_es_salaam']
        try:
            current_index = stages.index(self.current_route_stage)
            return ((current_index + 1) / len(stages)) * 100
        except ValueError:
            return 0
    
    @property
    def is_delivered(self):
        return self.status == 'delivered'
    




class PackingList(models.Model):
    """Simple Packing List - Stores only PDF files"""
    
    # Auto-generated code
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # code = models.CharField(max_length=20, unique=True)
    
    # Date
    date = models.DateField(default=timezone.now)
    
    # Creator (staff who created the list)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='packing_lists'
    )
    
    # Summary data (for display without opening PDF)
    total_cartons = models.IntegerField(default=0)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # PDF file (uploaded from Flutter)
    pdf_file = models.FileField(upload_to='packing_lists/%Y/%m/', max_length=500)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Packing List'
        verbose_name_plural = 'Packing Lists'
    
    def __str__(self):
        return f"{self.unique_id} - {self.date}"
