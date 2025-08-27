from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from datetime import datetime, timedelta
import uuid

from .models import Payment, PaymentMethod
from orders.models import Order
from .serializers import (
    PaymentMethodSerializer, PaymentInitializationSerializer,
    PaymentInitializationResponseSerializer, MobilePaymentSerializer,
    MobilePaymentResponseSerializer, PaymentStatusSerializer,
    PaymentSerializer
)


class PaymentMethodsView(APIView):
    """
    Get available payment methods
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get available payment methods",
        description="Retrieve available payment methods for the user",
        parameters=[
            OpenApiParameter(
                name='country',
                description='Filter by country code (e.g., TZ, US)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='currency',
                description='Filter by currency code (e.g., TZS, USD)',
                required=False,
                type=str
            ),
        ],
        responses={
            200: PaymentMethodSerializer(many=True),
        }
    )
    def get(self, request):
        # Get payment methods from database
        country = request.query_params.get('country', 'TZ')
        currency = request.query_params.get('currency', 'TZS')
        
        queryset = PaymentMethod.objects.filter(is_active=True)
        
        # For SQLite compatibility, we'll filter in Python instead of using contains lookup
        payment_methods = []
        
        for method in queryset.order_by('sort_order', 'name'):
            # Check country restriction
            if country and method.allowed_countries:
                if country not in method.allowed_countries:
                    continue
            
            # Check currency support
            if currency and method.supported_currencies:
                if currency not in method.supported_currencies:
                    continue
            
            payment_methods.append(method)
        
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(serializer.data)


class PaymentInitializationView(APIView):
    """
    Initialize payment for an order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Initialize payment",
        description="Initialize payment for an order",
        request=PaymentInitializationSerializer,
        responses={
            200: PaymentInitializationResponseSerializer,
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Order not found"),
        }
    )
    def post(self, request):
        serializer = PaymentInitializationSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            payment_method = serializer.validated_data['payment_method']
            return_url = serializer.validated_data.get('return_url')
            cancel_url = serializer.validated_data.get('cancel_url')
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                
                # Create payment record
                payment = Payment.objects.create(
                    order=order,
                    amount=order.total_amount,
                    currency=order.currency,
                    provider=payment_method['provider'],
                    method=payment_method['method'],
                    status='pending'
                )
                
                # Simulate payment provider integration
                if payment_method['provider'] == 'stripe':
                    response_data = {
                        'payment_id': str(payment.id),
                        'status': 'pending',
                        'payment_url': f"https://checkout.stripe.com/session_{uuid.uuid4().hex[:8]}",
                        'client_secret': f"pi_{uuid.uuid4().hex[:10]}_secret_{uuid.uuid4().hex[:6]}",
                        'provider_data': {
                            'session_id': f"cs_test_{uuid.uuid4().hex[:8]}",
                            'publishable_key': 'pk_test_123'
                        },
                        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
                    }
                elif payment_method['provider'] == 'paypal':
                    response_data = {
                        'payment_id': str(payment.id),
                        'status': 'pending',
                        'payment_url': f"https://www.paypal.com/checkoutnow?token={uuid.uuid4().hex[:16]}",
                        'provider_data': {
                            'token': uuid.uuid4().hex[:16]
                        },
                        'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
                    }
                else:
                    # For mobile money, we'll handle it in the mobile payment endpoint
                    response_data = {
                        'payment_id': str(payment.id),
                        'status': 'pending',
                        'message': 'Use mobile payment endpoint for mobile money payments'
                    }
                
                return Response(response_data)
                
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MobilePaymentView(APIView):
    """
    Process mobile money payments
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Process mobile money payment",
        description="Process mobile money payments (M-Pesa, Airtel Money, etc.)",
        request=MobilePaymentSerializer,
        responses={
            200: MobilePaymentResponseSerializer,
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Order not found"),
        }
    )
    def post(self, request):
        serializer = MobilePaymentSerializer(data=request.data)
        if serializer.is_valid():
            order_id = serializer.validated_data['order_id']
            payment_method = serializer.validated_data['payment_method']
            phone_number = serializer.validated_data['phone_number']
            
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                
                # Create or get existing payment record
                payment, created = Payment.objects.get_or_create(
                    order=order,
                    provider=payment_method['provider'],
                    method=payment_method['method'],
                    defaults={
                        'amount': order.total_amount,
                        'currency': order.currency,
                        'status': 'pending'
                    }
                )
                
                # Update status to processing
                payment.status = 'processing'
                payment.save()
                
                # Simulate mobile money provider integration
                provider_ref = f"MP{uuid.uuid4().hex[:8].upper()}"
                
                response_data = {
                    'payment_id': str(payment.id),
                    'status': 'processing',
                    'message': f"Payment request sent to your phone. Please check your {payment_method['method'].replace('_', '-').title()} and enter your PIN to complete the payment.",
                    'reference': provider_ref,
                    'instructions': f"Enter your {payment_method['method'].replace('_', '-').title()} PIN when prompted on your phone",
                    'timeout': 300,
                    'status_check_url': f"/api/v1/payments/{payment.id}/status/"
                }
                
                return Response(response_data)
                
            except Order.DoesNotExist:
                return Response(
                    {"error": "Order not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentStatusView(APIView):
    """
    Check payment status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Check payment status",
        description="Check the current status of a payment",
        responses={
            200: PaymentStatusSerializer,
            404: OpenApiResponse(description="Payment not found"),
        }
    )
    def get(self, request, payment_id):
        try:
            payment = Payment.objects.get(
                id=payment_id, 
                order__user=request.user
            )
            
            # Simulate status update (in real implementation, you'd check with the provider)
            import random
            if payment.status == 'processing' and random.choice([True, False, False]):
                # Simulate payment completion
                payment.status = 'completed'
                payment.processed_at = datetime.now()
                payment.provider_ref = f"TXN{uuid.uuid4().hex[:10].upper()}"
                payment.save()
                
                # Update order status
                payment.order.status = 'confirmed'
                payment.order.save()
            
            if payment.status == 'completed':
                response_data = {
                    'payment_id': str(payment.id),
                    'status': payment.status,
                    'order_id': str(payment.order.id),
                    'amount': str(payment.amount),
                    'currency': payment.currency,
                    'provider_ref': payment.provider_ref,
                    'processed_at': payment.processed_at.isoformat() if payment.processed_at else None,
                    'receipt_url': f"https://payments.example.com/receipt/{payment.id}"
                }
            elif payment.status == 'failed':
                response_data = {
                    'payment_id': str(payment.id),
                    'status': payment.status,
                    'order_id': str(payment.order.id),
                    'failure_reason': 'Insufficient funds',  # This would come from provider
                    'failure_code': 'INSUFFICIENT_FUNDS',
                    'retry_allowed': True
                }
            else:
                response_data = {
                    'payment_id': str(payment.id),
                    'status': payment.status,
                    'order_id': str(payment.order.id),
                }
            
            return Response(response_data)
            
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class PaymentListView(generics.ListAPIView):
    """
    List payments for the authenticated user
    """
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user).order_by('-created_at')
