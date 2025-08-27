from rest_framework import serializers
from .models import Payment, PaymentMethod


class PaymentMethodSerializer(serializers.ModelSerializer):
    fees = serializers.SerializerMethodField()
    icon = serializers.CharField(source='icon_url', read_only=True)
    
    class Meta:
        model = PaymentMethod
        fields = [
            'provider', 'method', 'name', 'description', 'icon', 'fees',
            'supported_currencies', 'is_active'
        ]
    
    def get_fees(self, obj):
        return {
            'percentage': float(obj.fee_percentage),
            'fixed_amount': str(obj.fixed_fee_amount)
        }


class PaymentInitializationSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.DictField()
    return_url = serializers.URLField(required=False)
    cancel_url = serializers.URLField(required=False)


class PaymentInitializationResponseSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    status = serializers.CharField()
    payment_url = serializers.URLField(required=False)
    client_secret = serializers.CharField(required=False)
    provider_data = serializers.DictField(required=False)
    expires_at = serializers.DateTimeField(required=False)


class MobilePaymentSerializer(serializers.Serializer):
    order_id = serializers.UUIDField()
    payment_method = serializers.DictField()
    phone_number = serializers.CharField(max_length=15)


class MobilePaymentResponseSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    status = serializers.CharField()
    message = serializers.CharField()
    reference = serializers.CharField(required=False)
    instructions = serializers.CharField(required=False)
    timeout = serializers.IntegerField(required=False)
    status_check_url = serializers.CharField(required=False)


class PaymentStatusSerializer(serializers.Serializer):
    payment_id = serializers.CharField()
    status = serializers.CharField()
    order_id = serializers.UUIDField(required=False)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    currency = serializers.CharField(required=False)
    provider_ref = serializers.CharField(required=False)
    processed_at = serializers.DateTimeField(required=False)
    receipt_url = serializers.URLField(required=False)
    failure_reason = serializers.CharField(required=False)
    failure_code = serializers.CharField(required=False)
    retry_allowed = serializers.BooleanField(required=False)


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'id', 'order', 'amount', 'currency', 'provider', 'method',
            'status', 'provider_ref', 'provider_data', 'failure_reason',
            'failure_code', 'created_at', 'updated_at', 'processed_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'processed_at']
