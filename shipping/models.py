from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class ShippingMethod(models.Model):
    """Shipping method configuration"""
    
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    carrier = models.CharField(_('carrier'), max_length=50)
    
    # Pricing
    base_cost = models.DecimalField(_('base cost'), max_digits=8, decimal_places=2)
    cost_per_kg = models.DecimalField(_('cost per kg'), max_digits=8, decimal_places=2, default=0)
    
    # Delivery estimates
    min_delivery_days = models.PositiveIntegerField(_('minimum delivery days'))
    max_delivery_days = models.PositiveIntegerField(_('maximum delivery days'))
    
    # Constraints
    max_weight = models.DecimalField(_('max weight (kg)'), max_digits=8, decimal_places=3, null=True, blank=True)
    max_dimensions = models.CharField(_('max dimensions (LxWxH cm)'), max_length=50, blank=True)
    
    # Geographic coverage
    domestic_only = models.BooleanField(_('domestic only'), default=True)
    supported_countries = models.JSONField(_('supported countries'), default=list, blank=True)
    
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'shipping_methods'
        verbose_name = _('Shipping Method')
        verbose_name_plural = _('Shipping Methods')
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.carrier})"
    
    def calculate_cost(self, weight, destination_country='TZ'):
        """Calculate shipping cost based on weight and destination"""
        if self.domestic_only and destination_country != 'TZ':
            return None
        
        if destination_country != 'TZ' and destination_country not in self.supported_countries:
            return None
        
        if self.max_weight and weight > self.max_weight:
            return None
        
        from decimal import Decimal, ROUND_HALF_UP
        weight_decimal = Decimal(str(weight))
        cost = self.base_cost + (self.cost_per_kg * weight_decimal)
        return cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


class Shipment(models.Model):
    """Shipment tracking model"""
    
    PENDING = 'pending'
    LABELED = 'labeled'
    PICKED_UP = 'picked_up'
    IN_TRANSIT = 'in_transit'
    OUT_FOR_DELIVERY = 'out_for_delivery'
    DELIVERED = 'delivered'
    RETURNED = 'returned'
    LOST = 'lost'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (LABELED, _('Label Created')),
        (PICKED_UP, _('Picked Up')),
        (IN_TRANSIT, _('In Transit')),
        (OUT_FOR_DELIVERY, _('Out for Delivery')),
        (DELIVERED, _('Delivered')),
        (RETURNED, _('Returned')),
        (LOST, _('Lost')),
        (CANCELLED, _('Cancelled')),
    ]
    
    # Shipment identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Order relationship
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='shipment')
    
    # Shipping details
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE)
    carrier = models.CharField(_('carrier'), max_length=50)
    tracking_number = models.CharField(_('tracking number'), max_length=100, unique=True)
    
    # Label information
    label_url = models.URLField(_('shipping label URL'), blank=True)
    label_format = models.CharField(_('label format'), max_length=10, default='PDF')
    
    # Package details
    weight = models.DecimalField(_('weight (kg)'), max_digits=8, decimal_places=3)
    dimensions = models.CharField(_('dimensions (LxWxH cm)'), max_length=50, blank=True)
    declared_value = models.DecimalField(_('declared value'), max_digits=10, decimal_places=2)
    
    # Shipping addresses (snapshot from order)
    from_address = models.JSONField(_('from address'))
    to_address = models.JSONField(_('to address'))
    
    # Status and tracking
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Cost
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=8, decimal_places=2)
    insurance_cost = models.DecimalField(_('insurance cost'), max_digits=8, decimal_places=2, default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    # Delivery confirmation
    delivered_to = models.CharField(_('delivered to'), max_length=200, blank=True)
    delivery_signature = models.CharField(_('delivery signature'), max_length=200, blank=True)
    delivery_photo_url = models.URLField(_('delivery photo URL'), blank=True)
    
    class Meta:
        db_table = 'shipments'
        verbose_name = _('Shipment')
        verbose_name_plural = _('Shipments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['tracking_number']),
            models.Index(fields=['status']),
            models.Index(fields=['carrier', 'status']),
        ]
    
    def __str__(self):
        return f"Shipment {self.tracking_number} - Order {self.order.order_number}"


class ShipmentEvent(models.Model):
    """Shipment tracking events"""
    
    shipment = models.ForeignKey(Shipment, on_delete=models.CASCADE, related_name='events')
    
    event_type = models.CharField(_('event type'), max_length=50)
    description = models.TextField(_('description'))
    location = models.CharField(_('location'), max_length=200, blank=True)
    
    # Event timing
    occurred_at = models.DateTimeField(_('occurred at'))
    recorded_at = models.DateTimeField(_('recorded at'), auto_now_add=True)
    
    # Source of the event
    source = models.CharField(_('source'), max_length=50, default='carrier')  # carrier, manual, system
    
    # Additional data from carrier
    raw_data = models.JSONField(_('raw event data'), default=dict, blank=True)
    
    class Meta:
        db_table = 'shipment_events'
        verbose_name = _('Shipment Event')
        verbose_name_plural = _('Shipment Events')
        ordering = ['-occurred_at']
        indexes = [
            models.Index(fields=['shipment', 'occurred_at']),
            models.Index(fields=['event_type']),
        ]
    
    def __str__(self):
        return f"{self.shipment.tracking_number} - {self.event_type}"


class ShippingRate(models.Model):
    """Shipping rate tables for different zones"""
    
    shipping_method = models.ForeignKey(ShippingMethod, on_delete=models.CASCADE, related_name='rates')
    
    # Geographic zone
    country = models.CharField(_('country'), max_length=2)  # ISO country code
    region = models.CharField(_('region'), max_length=100, blank=True)  # Optional sub-region
    
    # Weight-based pricing
    min_weight = models.DecimalField(_('minimum weight (kg)'), max_digits=8, decimal_places=3, default=0)
    max_weight = models.DecimalField(_('maximum weight (kg)'), max_digits=8, decimal_places=3)
    
    # Pricing
    base_rate = models.DecimalField(_('base rate'), max_digits=8, decimal_places=2)
    per_kg_rate = models.DecimalField(_('per kg rate'), max_digits=8, decimal_places=2, default=0)
    
    # Service level
    service_level = models.CharField(_('service level'), max_length=50, default='standard')  # standard, express, overnight
    
    # Delivery estimates for this zone
    min_delivery_days = models.PositiveIntegerField(_('minimum delivery days'))
    max_delivery_days = models.PositiveIntegerField(_('maximum delivery days'))
    
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'shipping_rates'
        verbose_name = _('Shipping Rate')
        verbose_name_plural = _('Shipping Rates')
        unique_together = ['shipping_method', 'country', 'service_level', 'min_weight', 'max_weight']
        indexes = [
            models.Index(fields=['country', 'service_level']),
            models.Index(fields=['shipping_method', 'country']),
        ]
    
    def __str__(self):
        return f"{self.shipping_method.name} - {self.country} ({self.min_weight}-{self.max_weight}kg)"
    
    def calculate_cost(self, weight):
        """Calculate cost for this rate given a weight"""
        if weight < self.min_weight or weight > self.max_weight:
            return None
        
        return self.base_rate + (self.per_kg_rate * weight)
