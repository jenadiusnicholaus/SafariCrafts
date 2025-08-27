from django.urls import path
from . import views

app_name = 'shipping'

urlpatterns = [
    # Shipping methods
    path('methods/', views.ShippingMethodListView.as_view(), name='shipping_methods'),
    path('calculate/', views.ShippingCostCalculationView.as_view(), name='calculate_shipping'),
    
    # Shipments
    path('shipments/', views.ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
]
