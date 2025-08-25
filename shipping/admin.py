from django.contrib import admin
from .models import ShippingMethod, Shipment, ShipmentEvent, ShippingRate


@admin.register(ShippingMethod)
class ShippingMethodAdmin(admin.ModelAdmin):
    """ShippingMethod admin"""
    list_display = ('name', 'carrier', 'is_active')
    list_filter = ('carrier', 'is_active')
    search_fields = ('name', 'carrier')
    ordering = ('name',)


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    """ShippingRate admin"""
    list_display = ('shipping_method', 'base_rate', 'per_kg_rate')
    search_fields = ('shipping_method__name',)
    ordering = ('shipping_method',)


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    """Shipment admin"""
    list_display = ('tracking_number', 'order', 'shipping_method', 'status')
    list_filter = ('shipping_method', 'status')
    search_fields = ('tracking_number', 'order__order_number')
    ordering = ('-created_at',)


@admin.register(ShipmentEvent)
class ShipmentEventAdmin(admin.ModelAdmin):
    """ShipmentEvent admin"""
    list_display = ('shipment', 'event_type', 'location')
    list_filter = ('event_type',)
    search_fields = ('shipment__tracking_number', 'location')
    ordering = ('-occurred_at',)
