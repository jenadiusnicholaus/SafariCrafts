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
    AZAMPAY = 'azampay'
    
    PROVIDER_CHOICES = [
        (STRIPE, _('Stripe')),
        (PAYPAL, _('PayPal')),
        (DPO, _('DPO')),
        (SELCOM, _('Selcom')),
        (PESAPAL, _('PesaPal')),
        (AZAMPAY, _('Azam Pay')),
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
    """Payment method configuration"""
    
    # Payment Providers
    STRIPE = 'stripe'
    PAYPAL = 'paypal'
    DPO = 'dpo'
    SELCOM = 'selcom'
    PESAPAL = 'pesapal'
    AZAMPAY = 'azampay'
    
    PROVIDER_CHOICES = [
        (STRIPE, _('Stripe')),
        (PAYPAL, _('PayPal')),
        (DPO, _('DPO')),
        (SELCOM, _('Selcom')),
        (PESAPAL, _('PesaPal')),
        (AZAMPAY, _('Azam Pay')),
    ]
    
    # Payment Methods
    CARD = 'card'
    MPESA = 'mpesa'
    AIRTEL_MONEY = 'airtel_money'
    TIGO_PESA = 'tigo_pesa'
    BANK_TRANSFER = 'bank_transfer'
    PAYPAL = 'paypal'
    
    METHOD_CHOICES = [
        (CARD, _('Credit/Debit Card')),
        (MPESA, _('M-Pesa')),
        (AIRTEL_MONEY, _('Airtel Money')),
        (TIGO_PESA, _('Tigo Pesa')),
        (BANK_TRANSFER, _('Bank Transfer')),
        (PAYPAL, _('PayPal')),
    ]
    
    # Basic information
    provider = models.CharField(_('provider'), max_length=20, choices=PROVIDER_CHOICES)
    method = models.CharField(_('method'), max_length=20, choices=METHOD_CHOICES, default=METHOD_CHOICES[0][0])
    name = models.CharField(_('display name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    icon_url = models.URLField(_('icon URL'), blank=True)
    
    # Fees and costs
    fee_percentage = models.DecimalField(
        _('fee percentage'), 
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text=_('Fee as percentage (e.g., 3.5 for 3.5%)')
    )
    fixed_fee_amount = models.DecimalField(
        _('fixed fee amount'), 
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        help_text=_('Fixed fee amount in base currency')
    )
    
    # Currency support
    supported_currencies = models.JSONField(
        _('supported currencies'), 
        default=list,
        help_text=_('List of supported currency codes (e.g., ["USD", "TZS"])')
    )
    
    # Availability
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    # Geographic restrictions
    allowed_countries = models.JSONField(
        _('allowed countries'), 
        default=list, 
        blank=True,
        help_text=_('List of country codes where this method is available. Empty means all countries.')
    )
    
    # Configuration
    configuration = models.JSONField(
        _('provider configuration'), 
        default=dict, 
        blank=True,
        help_text=_('Provider-specific configuration (API keys, endpoints, etc.)')
    )
    
    # Metadata
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'payment_methods'
        verbose_name = _('Payment Method')
        verbose_name_plural = _('Payment Methods')
        ordering = ['sort_order', 'name']
        unique_together = ['provider', 'method']
        indexes = [
            models.Index(fields=['provider', 'method']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.provider})"
    
    def calculate_fee(self, amount):
        """Calculate fee for given amount"""
        percentage_fee = amount * (self.fee_percentage / 100)
        total_fee = percentage_fee + self.fixed_fee_amount
        return total_fee
    
    def is_available_in_country(self, country_code):
        """Check if payment method is available in specific country"""
        if not self.allowed_countries:
            return True  # Available everywhere if no restrictions
        return country_code in self.allowed_countries
    
    def supports_currency(self, currency_code):
        """Check if payment method supports specific currency"""
        return currency_code in self.supported_currencies


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
