from django.urls import path
from . import views
from .webhooks.azam_pay import AzamPayWebhookView, azam_pay_webhook_simple

app_name = 'payments'

urlpatterns = [
    # Payment methods
    path('methods/', views.PaymentMethodsView.as_view(), name='payment_methods'),
    
    # Payment processing
    path('initialize/', views.PaymentInitializationView.as_view(), name='initialize_payment'),
    path('process-mobile/', views.MobilePaymentView.as_view(), name='process_mobile_payment'),
    
    # Payment status
    path('<uuid:payment_id>/status/', views.PaymentStatusView.as_view(), name='payment_status'),
    
    # Payment history
    path('', views.PaymentListView.as_view(), name='payment_list'),
    
    # Webhooks
    path('webhooks/azam-pay/', AzamPayWebhookView.as_view(), name='azam_pay_webhook'),
    path('webhooks/azam-pay/simple/', azam_pay_webhook_simple, name='azam_pay_webhook_simple'),
]
