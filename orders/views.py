from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from decimal import Decimal

from .models import Order, OrderItem, OrderStatusHistory
from .serializers import (
    OrderSerializer, OrderListSerializer, OrderCreateSerializer,
    OrderItemSerializer, OrderStatusHistorySerializer
)
from catalog.models import Cart, CartItem
from shipping.models import ShippingMethod
from django.contrib.auth import get_user_model

User = get_user_model()


class OrderCreateView(APIView):
    """
    Create order from user's cart
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Create order from cart",
        description="Convert cart to order with shipping and billing information",
        request=OrderCreateSerializer,
        responses={
            201: OrderSerializer,
            400: OpenApiResponse(description="Invalid input or empty cart"),
            404: OpenApiResponse(description="Shipping method not found"),
        }
    )
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            shipping_address = serializer.validated_data['shipping_address']
            billing_address = serializer.validated_data['billing_address']
            shipping_method_id = serializer.validated_data['shipping_method_id']
            customer_notes = serializer.validated_data.get('customer_notes', '')
            same_as_shipping = serializer.validated_data.get('same_as_shipping', False)
            
            # If same_as_shipping is True, use shipping address for billing
            if same_as_shipping:
                billing_address = shipping_address
            
            try:
                # Get user's cart
                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                
                if not cart_items.exists():
                    return Response(
                        {"error": "Cart is empty"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get shipping method
                shipping_method = ShippingMethod.objects.get(
                    id=shipping_method_id,
                    is_active=True
                )
                
                # Calculate totals
                subtotal = sum(item.total_price for item in cart_items)
                
                # Calculate shipping cost (you might want to get weight from cart items)
                shipping_cost = shipping_method.calculate_cost(2.5)  # Default weight
                
                # For now, no tax or discount
                tax_amount = Decimal('0.00')
                discount_amount = Decimal('0.00')
                
                total_amount = subtotal + shipping_cost + tax_amount - discount_amount
                
                # Create order in a transaction
                with transaction.atomic():
                    order = Order.objects.create(
                        user=request.user,
                        currency='TZS',
                        subtotal=subtotal,
                        shipping_cost=shipping_cost,
                        tax_amount=tax_amount,
                        discount_amount=discount_amount,
                        total_amount=total_amount,
                        shipping_address=shipping_address,
                        billing_address=billing_address,
                        shipping_method=shipping_method,
                        customer_notes=customer_notes,
                        status='pending'
                    )
                    
                    # Create order items from cart items
                    for cart_item in cart_items:
                        # Create snapshot of artwork data
                        artwork_snapshot = {
                            'title': cart_item.artwork.title,
                            'artist': cart_item.artwork.artist.user.get_full_name() if cart_item.artwork.artist else 'Unknown',
                            'price': str(cart_item.artwork.price),
                            'currency': cart_item.artwork.currency
                        }
                        
                        OrderItem.objects.create(
                            order=order,
                            artwork=cart_item.artwork,
                            quantity=cart_item.quantity,
                            unit_price=cart_item.artwork.price,
                            tax_rate=Decimal('0.0000'),  # No tax for now
                            snapshot=artwork_snapshot
                        )
                    
                    # Create initial status history
                    OrderStatusHistory.objects.create(
                        order=order,
                        new_status='pending',
                        notes='Order created'
                    )
                    
                    # Clear the cart
                    cart_items.delete()
                
                # Return the created order
                order_serializer = OrderSerializer(order, context={'request': request})
                return Response(order_serializer.data, status=status.HTTP_201_CREATED)
                
            except Cart.DoesNotExist:
                return Response(
                    {"error": "Cart not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except ShippingMethod.DoesNotExist:
                return Response(
                    {"error": "Shipping method not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderListView(generics.ListAPIView):
    """
    List orders for the authenticated user
    """
    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get user orders",
        description="Retrieve user's order history",
        parameters=[
            OpenApiParameter(
                name='status',
                description='Filter by order status',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='ordering',
                description='Sort order (-created_at, created_at, total_amount, etc.)',
                required=False,
                type=str
            ),
        ],
        responses={
            200: OrderListSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        
        # Filter by status if provided
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Apply ordering
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset


class OrderDetailView(generics.RetrieveAPIView):
    """
    Retrieve detailed order information
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    @extend_schema(
        summary="Get order details",
        description="Retrieve detailed order information",
        responses={
            200: OrderSerializer,
            404: OpenApiResponse(description="Order not found"),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderCancelView(APIView):
    """
    Cancel an order
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Cancel order",
        description="Cancel an order if it's still cancellable",
        responses={
            200: OpenApiResponse(description="Order cancelled successfully"),
            400: OpenApiResponse(description="Order cannot be cancelled"),
            404: OpenApiResponse(description="Order not found"),
        }
    )
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            
            # Check if order can be cancelled
            if order.status not in ['pending', 'confirmed']:
                return Response(
                    {"error": "Order cannot be cancelled"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Check if payment is already processed
            if hasattr(order, 'payment') and order.payment.status == 'completed':
                return Response(
                    {"error": "Order cannot be cancelled - payment already processed"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cancel the order
            order.status = 'cancelled'
            order.save()
            
            # Add status history
            OrderStatusHistory.objects.create(
                order=order,
                old_status=order.status,
                new_status='cancelled',
                notes='Order cancelled by customer'
            )
            
            return Response({"message": "Order cancelled successfully"})
            
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )


class OrderStatusHistoryView(generics.ListAPIView):
    """
    Get order status history
    """
    serializer_class = OrderStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        order_id = self.kwargs['order_id']
        return OrderStatusHistory.objects.filter(
            order__id=order_id,
            order__user=self.request.user
        ).order_by('changed_at')
