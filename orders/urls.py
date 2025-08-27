from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Order management
    path('create/', views.OrderCreateView.as_view(), name='order_create'),
    path('', views.OrderListView.as_view(), name='order_list'),
    path('<uuid:id>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<uuid:order_id>/cancel/', views.OrderCancelView.as_view(), name='order_cancel'),
    
    # Order status history
    path('<uuid:order_id>/history/', views.OrderStatusHistoryView.as_view(), name='order_history'),
]
