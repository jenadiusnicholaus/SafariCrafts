from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Order(models.Model):
    """Order model"""
    
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    PROCESSING = 'processing'
    SHIPPED = 'shipped'
    DELIVERED = 'delivered'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending Payment')),
        (CONFIRMED, _('Payment Confirmed')),
        (PROCESSING, _('Processing')),
        (SHIPPED, _('Shipped')),
        (DELIVERED, _('Delivered')),
        (COMPLETED, _('Completed')),
        (CANCELLED, _('Cancelled')),
        (REFUNDED, _('Refunded')),
    ]
    
    # Order identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(_('order number'), max_length=20, unique=True)
    
    # Customer information
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Order details
    status = models.CharField(_('status'), max_length=15, choices=STATUS_CHOICES, default=PENDING)
    currency = models.CharField(_('currency'), max_length=3, default='TZS')
    
    # Pricing
    subtotal = models.DecimalField(_('subtotal'), max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(_('shipping cost'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('tax amount'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('discount amount'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('total amount'), max_digits=10, decimal_places=2)
    
    # Addresses (stored as JSON to preserve data even if user changes their addresses)
    shipping_address = models.JSONField(_('shipping address'))
    billing_address = models.JSONField(_('billing address'))
    
    # Order notes
    customer_notes = models.TextField(_('customer notes'), blank=True)
    admin_notes = models.TextField(_('admin notes'), blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    shipped_at = models.DateTimeField(_('shipped at'), null=True, blank=True)
    delivered_at = models.DateTimeField(_('delivered at'), null=True, blank=True)
    
    class Meta:
        db_table = 'orders'
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['order_number']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status']),
        ]
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Generate order number (e.g., SC2024001234)
            from django.utils import timezone
            year = timezone.now().year
            last_order = Order.objects.filter(
                order_number__startswith=f'SC{year}'
            ).order_by('order_number').last()
            
            if last_order:
                last_num = int(last_order.order_number[-6:])
                new_num = last_num + 1
            else:
                new_num = 1
            
            self.order_number = f'SC{year}{new_num:06d}'
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"
    
    @property
    def is_paid(self):
        return hasattr(self, 'payment') and self.payment.status == 'completed'
    
    @property
    def can_be_cancelled(self):
        return self.status in [self.PENDING, self.CONFIRMED]
    
    @property
    def can_be_refunded(self):
        return self.status in [self.CONFIRMED, self.PROCESSING, self.SHIPPED] and self.is_paid


class OrderItem(models.Model):
    """Order item model"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey('catalog.Artwork', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('quantity'))
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('tax rate'), max_digits=5, decimal_places=4, default=0)
    
    # Snapshot of artwork data at time of order
    snapshot = models.JSONField(_('artwork snapshot'))
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'order_items'
        verbose_name = _('Order Item')
        verbose_name_plural = _('Order Items')
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['artwork']),
        ]
    
    def __str__(self):
        return f"{self.artwork.title} x {self.quantity} (Order {self.order.order_number})"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    @property
    def tax_amount(self):
        return self.total_price * self.tax_rate


class OrderStatusHistory(models.Model):
    """Track order status changes"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(_('old status'), max_length=15, blank=True)
    new_status = models.CharField(_('new status'), max_length=15)
    notes = models.TextField(_('notes'), blank=True)
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='order_status_changes'
    )
    changed_at = models.DateTimeField(_('changed at'), auto_now_add=True)
    
    class Meta:
        db_table = 'order_status_history'
        verbose_name = _('Order Status History')
        verbose_name_plural = _('Order Status Histories')
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"Order {self.order.order_number}: {self.old_status} → {self.new_status}"


class Refund(models.Model):
    """Refund model"""
    
    PENDING = 'pending'
    APPROVED = 'approved'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (APPROVED, _('Approved')),
        (PROCESSING, _('Processing')),
        (COMPLETED, _('Completed')),
        (REJECTED, _('Rejected')),
    ]
    
    FULL = 'full'
    PARTIAL = 'partial'
    
    TYPE_CHOICES = [
        (FULL, _('Full Refund')),
        (PARTIAL, _('Partial Refund')),
    ]
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    refund_type = models.CharField(_('refund type'), max_length=10, choices=TYPE_CHOICES)
    amount = models.DecimalField(_('refund amount'), max_digits=10, decimal_places=2)
    reason = models.TextField(_('reason'))
    status = models.CharField(_('status'), max_length=15, choices=STATUS_CHOICES, default=PENDING)
    
    # Processing information
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='processed_refunds'
    )
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    provider_ref = models.CharField(_('provider reference'), max_length=255, blank=True)
    
    # Notes
    admin_notes = models.TextField(_('admin notes'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'refunds'
        verbose_name = _('Refund')
        verbose_name_plural = _('Refunds')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund for Order {self.order.order_number} - {self.amount}"
