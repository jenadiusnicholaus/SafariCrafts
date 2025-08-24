from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Payment(models.Model):
    """Payment model"""
    
    # Payment Status
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    REFUNDED = 'refunded'
    PARTIALLY_REFUNDED = 'partially_refunded'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (PROCESSING, _('Processing')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed')),
        (CANCELLED, _('Cancelled')),
        (REFUNDED, _('Refunded')),
        (PARTIALLY_REFUNDED, _('Partially Refunded')),
    ]
    
    # Payment Providers
    STRIPE = 'stripe'
    PAYPAL = 'paypal'
    DPO = 'dpo'
    SELCOM = 'selcom'
    PESAPAL = 'pesapal'
    
    PROVIDER_CHOICES = [
        (STRIPE, _('Stripe')),
        (PAYPAL, _('PayPal')),
        (DPO, _('DPO')),
        (SELCOM, _('Selcom')),
        (PESAPAL, _('PesaPal')),
    ]
    
    # Payment Methods
    CARD = 'card'
    MPESA = 'mpesa'
    AIRTEL_MONEY = 'airtel_money'
    TIGO_PESA = 'tigo_pesa'
    BANK_TRANSFER = 'bank_transfer'
    PAYPAL_ACCOUNT = 'paypal_account'
    
    METHOD_CHOICES = [
        (CARD, _('Credit/Debit Card')),
        (MPESA, _('M-Pesa')),
        (AIRTEL_MONEY, _('Airtel Money')),
        (TIGO_PESA, _('Tigo Pesa')),
        (BANK_TRANSFER, _('Bank Transfer')),
        (PAYPAL_ACCOUNT, _('PayPal Account')),
    ]
    
    # Payment identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Order relationship
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    
    # Payment details
    provider = models.CharField(_('payment provider'), max_length=20, choices=PROVIDER_CHOICES)
    provider_ref = models.CharField(_('provider reference'), max_length=255, unique=True)
    method = models.CharField(_('payment method'), max_length=20, choices=METHOD_CHOICES)
    
    # Amount details
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3)
    exchange_rate = models.DecimalField(_('exchange rate'), max_digits=10, decimal_places=6, null=True, blank=True)
    
    # Status and processing
    status = models.CharField(_('status'), max_length=20, choices=STATUS_CHOICES, default=PENDING)
    
    # Provider-specific metadata
    provider_data = models.JSONField(_('provider data'), default=dict, blank=True)
    
    # Failure information
    failure_reason = models.TextField(_('failure reason'), blank=True)
    failure_code = models.CharField(_('failure code'), max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payments'
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider_ref']),
            models.Index(fields=['status']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payment {self.id} - Order {self.order.order_number} - {self.status}"
    
    @property
    def is_successful(self):
        return self.status == self.COMPLETED
    
    @property
    def can_be_refunded(self):
        return self.status in [self.COMPLETED, self.PARTIALLY_REFUNDED]


class PaymentMethod(models.Model):
    """Saved payment methods for users"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_methods')
    provider = models.CharField(_('provider'), max_length=20, choices=Payment.PROVIDER_CHOICES)
    method_type = models.CharField(_('method type'), max_length=20, choices=Payment.METHOD_CHOICES)
    
    # Payment method details (stored securely)
    provider_method_id = models.CharField(_('provider method ID'), max_length=255)
    
    # Display information
    display_name = models.CharField(_('display name'), max_length=100)
    last_four = models.CharField(_('last four digits'), max_length=4, blank=True)
    
    # Metadata
    metadata = models.JSONField(_('metadata'), default=dict, blank=True)
    
    is_default = models.BooleanField(_('is default'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        unique_together = ['user', 'provider_method_id']
    
    def __str__(self):
        return f"{self.user.email} - {self.display_name}"


class PaymentWebhook(models.Model):
    """Store webhook events from payment providers"""
    
    provider = models.CharField(_('provider'), max_length=20, choices=Payment.PROVIDER_CHOICES)
    event_id = models.CharField(_('event ID'), max_length=255, unique=True)
    event_type = models.CharField(_('event type'), max_length=100)
    
    # Webhook data
    raw_data = models.JSONField(_('raw webhook data'))
    
    # Processing status
    processed = models.BooleanField(_('processed'), default=False)
    processing_attempts = models.PositiveIntegerField(_('processing attempts'), default=0)
    last_processing_error = models.TextField(_('last processing error'), blank=True)
    
    # Related payment (if applicable)
    payment = models.ForeignKey(
        Payment, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='webhook_events'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payment_webhooks'
        verbose_name = _('Payment Webhook')
        verbose_name_plural = _('Payment Webhooks')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['provider', 'event_type']),
            models.Index(fields=['processed']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Webhook {self.event_id} - {self.provider} - {self.event_type}"


class PaymentRefund(models.Model):
    """Payment refund tracking"""
    
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (PROCESSING, _('Processing')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed')),
        (CANCELLED, _('Cancelled')),
    ]
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund = models.OneToOneField('orders.Refund', on_delete=models.CASCADE, related_name='payment_refund')
    
    amount = models.DecimalField(_('refund amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3)
    
    provider_refund_id = models.CharField(_('provider refund ID'), max_length=255, blank=True)
    status = models.CharField(_('status'), max_length=15, choices=STATUS_CHOICES, default=PENDING)
    
    failure_reason = models.TextField(_('failure reason'), blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    class Meta:
        db_table = 'payment_refunds'
        verbose_name = _('Payment Refund')
        verbose_name_plural = _('Payment Refunds')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Refund {self.id} - Payment {self.payment.id} - {self.amount}"
