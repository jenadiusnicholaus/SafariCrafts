from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse
from datetime import date, timedelta

from .models import ShippingMethod, Shipment
from .serializers import (
    ShippingMethodSerializer, ShippingCostCalculationSerializer,
    ShippingCostResponseSerializer, ShipmentSerializer
)


class ShippingMethodListView(generics.ListAPIView):
    """
    Get available shipping methods for checkout
    """
    serializer_class = ShippingMethodSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Get available shipping methods",
        description="Retrieve available shipping methods with cost calculation",
        parameters=[
            OpenApiParameter(
                name='country',
                description='Destination country code',
                required=False,
                type=str,
                default='TZ'
            ),
            OpenApiParameter(
                name='weight',
                description='Total weight in kg for cost calculation',
                required=False,
                type=float
            ),
        ],
        responses={
            200: ShippingMethodSerializer(many=True),
        }
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    def get_queryset(self):
        country = self.request.query_params.get('country', 'TZ')
        
        # Filter by country availability
        queryset = ShippingMethod.objects.filter(is_active=True)
        
        if country != 'TZ':
            # For international shipping
            queryset = queryset.filter(
                models.Q(domestic_only=False) | 
                models.Q(supported_countries__contains=[country])
            )
        
        return queryset
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        weight = self.request.query_params.get('weight')
        if weight:
            try:
                context['weight'] = float(weight)
            except (ValueError, TypeError):
                pass
        return context


class ShippingCostCalculationView(APIView):
    """
    Calculate shipping cost for specific method and parameters
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Calculate shipping cost",
        description="Calculate shipping cost for specific method and cart",
        request=ShippingCostCalculationSerializer,
        responses={
            200: ShippingCostResponseSerializer,
            400: OpenApiResponse(description="Invalid input"),
            404: OpenApiResponse(description="Shipping method not found"),
        }
    )
    def post(self, request):
        serializer = ShippingCostCalculationSerializer(data=request.data)
        if serializer.is_valid():
            method_id = serializer.validated_data['shipping_method_id']
            country = serializer.validated_data['country']
            weight = serializer.validated_data['weight']
            
            try:
                shipping_method = ShippingMethod.objects.get(
                    id=method_id, 
                    is_active=True
                )
                
                # Check if method supports the country
                if country != 'TZ' and shipping_method.domestic_only:
                    if country not in shipping_method.supported_countries:
                        return Response(
                            {"error": "Shipping method not available for this country"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                
                # Check weight limit
                if weight > shipping_method.max_weight:
                    return Response(
                        {"error": f"Weight exceeds maximum limit of {shipping_method.max_weight}kg"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                cost = shipping_method.calculate_cost(weight)
                estimated_date = date.today() + timedelta(days=shipping_method.max_delivery_days)
                delivery_window = f"{shipping_method.min_delivery_days}-{shipping_method.max_delivery_days} business days"
                
                response_data = {
                    'shipping_method': {
                        'id': shipping_method.id,
                        'name': shipping_method.name,
                        'carrier': shipping_method.carrier
                    },
                    'cost': str(cost),
                    'currency': 'TZS',
                    'estimated_delivery_date': estimated_date,
                    'delivery_window': delivery_window
                }
                
                return Response(response_data)
                
            except ShippingMethod.DoesNotExist:
                return Response(
                    {"error": "Shipping method not found"},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ShipmentListView(generics.ListCreateAPIView):
    """
    List shipments for the authenticated user or create new shipment
    """
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Shipment.objects.filter(order__user=self.request.user)


class ShipmentDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update specific shipment
    """
    serializer_class = ShipmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Shipment.objects.filter(order__user=self.request.user)
