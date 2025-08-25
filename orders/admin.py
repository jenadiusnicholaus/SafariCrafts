from django.contrib import admin
from .models import Order, OrderItem, OrderStatusHistory, Refund


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Order admin"""
    list_display = ('order_number', 'user', 'status', 'total_amount', 'currency')
    list_filter = ('status', 'currency')
    search_fields = ('order_number', 'user__email', 'user__first_name', 'user__last_name')
    ordering = ('-created_at',)


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """OrderItem admin"""
    list_display = ('order', 'artwork', 'quantity')
    search_fields = ('order__order_number', 'artwork__title')
    ordering = ('-created_at',)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    """OrderStatusHistory admin"""
    list_display = ('order', 'old_status', 'new_status', 'changed_by')
    list_filter = ('old_status', 'new_status')
    search_fields = ('order__order_number', 'changed_by__email')
    ordering = ('-changed_at',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    """Refund admin"""
    list_display = ('order', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('order__order_number',)
    ordering = ('-created_at',)
