from rest_framework import serializers
from .models import Order, OrderItem, OrderStatusHistory
from catalog.serializers import ArtworkListSerializer
from shipping.serializers import ShippingMethodSerializer, ShipmentSerializer
from payments.serializers import PaymentSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    artwork = ArtworkListSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'artwork', 'quantity', 'unit_price', 'total_price',
            'tax_rate', 'tax_amount', 'snapshot'
        ]
        read_only_fields = ['id', 'total_price', 'tax_amount']


class OrderCreateSerializer(serializers.Serializer):
    shipping_address = serializers.DictField()
    billing_address = serializers.DictField()
    shipping_method_id = serializers.IntegerField()
    customer_notes = serializers.CharField(max_length=500, required=False, allow_blank=True)
    same_as_shipping = serializers.BooleanField(default=False)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    shipping_method = ShippingMethodSerializer(read_only=True)
    payment = PaymentSerializer(read_only=True)
    shipment = ShipmentSerializer(read_only=True)
    status_history = serializers.SerializerMethodField()
    payment_required = serializers.SerializerMethodField()
    is_paid = serializers.SerializerMethodField()
    can_be_cancelled = serializers.SerializerMethodField()
    can_be_refunded = serializers.SerializerMethodField()
    items_count = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    shipment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'currency', 'subtotal',
            'shipping_cost', 'tax_amount', 'discount_amount', 'total_amount',
            'shipping_address', 'billing_address', 'items', 'shipping_method',
            'payment', 'shipment', 'status_history', 'customer_notes',
            'created_at', 'updated_at', 'payment_required', 'is_paid',
            'can_be_cancelled', 'can_be_refunded', 'items_count',
            'payment_status', 'shipment_status', 'delivered_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'created_at', 'updated_at',
            'payment_required', 'is_paid', 'can_be_cancelled',
            'can_be_refunded', 'items_count', 'payment_status',
            'shipment_status'
        ]
    
    def get_status_history(self, obj):
        history = OrderStatusHistory.objects.filter(order=obj).order_by('changed_at')
        return [
            {
                'old_status': h.old_status,
                'new_status': h.new_status,
                'changed_at': h.changed_at,
                'notes': h.notes
            }
            for h in history
        ]
    
    def get_payment_required(self, obj):
        return obj.total_amount > 0
    
    def get_is_paid(self, obj):
        return hasattr(obj, 'payment') and obj.payment.status == 'completed'
    
    def get_can_be_cancelled(self, obj):
        return obj.status in ['pending', 'confirmed'] and not self.get_is_paid(obj)
    
    def get_can_be_refunded(self, obj):
        return obj.status in ['confirmed', 'processing', 'shipped'] and self.get_is_paid(obj)
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_payment_status(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.status
        return None
    
    def get_shipment_status(self, obj):
        if hasattr(obj, 'shipment'):
            return obj.shipment.status
        return None


class OrderListSerializer(serializers.ModelSerializer):
    items_count = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()
    shipment_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'status', 'total_amount', 'currency',
            'items_count', 'created_at', 'delivered_at', 'payment_status',
            'shipment_status'
        ]
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def get_payment_status(self, obj):
        if hasattr(obj, 'payment'):
            return obj.payment.status
        return None
    
    def get_shipment_status(self, obj):
        if hasattr(obj, 'shipment'):
            return obj.shipment.status
        return None


class OrderStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderStatusHistory
        fields = ['id', 'order', 'old_status', 'new_status', 'notes', 'changed_by', 'changed_at']
        read_only_fields = ['id', 'changed_at']
