from rest_framework import serializers
from .models import ShippingMethod, Shipment


class ShippingMethodSerializer(serializers.ModelSerializer):
    calculated_cost = serializers.SerializerMethodField()
    estimated_delivery = serializers.SerializerMethodField()
    
    class Meta:
        model = ShippingMethod
        fields = [
            'id', 'name', 'description', 'carrier', 'base_cost', 
            'cost_per_kg', 'calculated_cost', 'min_delivery_days', 
            'max_delivery_days', 'max_weight', 'max_dimensions',
            'domestic_only', 'supported_countries', 'is_active',
            'estimated_delivery'
        ]
        read_only_fields = ['calculated_cost', 'estimated_delivery']
    
    def get_calculated_cost(self, obj):
        # Get weight from context if provided
        weight = self.context.get('weight', 0)
        if weight:
            return obj.calculate_cost(weight)
        return obj.base_cost
    
    def get_estimated_delivery(self, obj):
        from datetime import date, timedelta
        min_date = date.today() + timedelta(days=obj.min_delivery_days)
        max_date = date.today() + timedelta(days=obj.max_delivery_days)
        return f"{min_date} to {max_date}"


class ShippingCostCalculationSerializer(serializers.Serializer):
    shipping_method_id = serializers.IntegerField()
    country = serializers.CharField(max_length=2, default='TZ')
    weight = serializers.DecimalField(max_digits=10, decimal_places=3)


class ShippingCostResponseSerializer(serializers.Serializer):
    shipping_method = serializers.DictField()
    cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField(default='TZS')
    estimated_delivery_date = serializers.DateField()
    delivery_window = serializers.CharField()


class ShipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'shipping_method', 'carrier', 'tracking_number',
            'status', 'weight', 'dimensions', 'declared_value',
            'shipping_cost', 'insurance_cost', 'shipped_at', 'delivered_at',
            'delivered_to', 'delivery_signature', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
