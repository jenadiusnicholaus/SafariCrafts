from django.contrib import admin
from .models import Payment, PaymentMethod, PaymentWebhook, PaymentRefund


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Payment admin"""
    list_display = ('id', 'order', 'amount', 'currency', 'status', 'provider')
    list_filter = ('status', 'provider', 'currency')
    search_fields = ('order__order_number', 'provider_ref')
    ordering = ('-created_at',)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    """System Payment Method admin"""
    list_display = ('name', 'provider', 'method', 'is_active', 'sort_order')
    list_filter = ('provider', 'method', 'is_active')
    search_fields = ('name', 'provider', 'method')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('provider', 'method', 'name', 'description', 'icon_url')
        }),
        ('Fees and Costs', {
            'fields': ('fee_percentage', 'fixed_fee_amount')
        }),
        ('Currency and Geography', {
            'fields': ('supported_currencies', 'allowed_countries')
        }),
        ('Availability', {
            'fields': ('is_active', 'sort_order')
        }),
        ('Configuration', {
            'fields': ('configuration',),
            'classes': ('collapse',)
        }),
    )


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
