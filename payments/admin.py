from django.contrib import admin
from .models import Payment, PaymentMethod, PaymentWebhook, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin"""
    list_display = ('id', 'order', 'amount', 'currency', 'status', 'provider')
    list_filter = ('status', 'provider', 'currency')
    search_fields = ('order__order_number', 'gateway_transaction_id')
    ordering = ('-created_at',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """PaymentMethod admin"""
    list_display = ('user', 'provider', 'is_default', 'is_active')
    list_filter = ('provider', 'is_default', 'is_active')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    """PaymentWebhook admin"""
    list_display = ('event_type', 'provider', 'processed')
    list_filter = ('event_type', 'provider', 'processed')
    search_fields = ('event_id', 'event_type')
    ordering = ('-created_at',)


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    """PaymentRefund admin"""
    list_display = ('payment', 'amount', 'currency', 'status')
    list_filter = ('status', 'currency')
    search_fields = ('payment__order__order_number',)
    ordering = ('-created_at',)
