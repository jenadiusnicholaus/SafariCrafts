"""
Azam Pay webhook handlers
"""
import json
import logging
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from payments.models import Payment, PaymentWebhook

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AzamPayWebhookView(APIView):
    """Handle Azam Pay webhook callbacks"""
    
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request):
        """Process Azam Pay webhook"""
        try:
            # Get webhook data
            webhook_data = request.data if hasattr(request, 'data') else json.loads(request.body)
            
            # Log webhook for debugging
            logger.info(f"Azam Pay webhook received: {webhook_data}")
            
            # Extract relevant fields
            transaction_id = webhook_data.get('transactionId')
            external_id = webhook_data.get('externalId')
            status_value = webhook_data.get('status') or webhook_data.get('transactionStatus')
            amount = webhook_data.get('amount')
            
            if not external_id:
                logger.error("No external_id found in webhook data")
                return Response({"error": "Missing external_id"}, status=400)
            
            # Find the payment by external_id (which should be the payment ID)
            try:
                payment = Payment.objects.get(id=external_id)
            except Payment.DoesNotExist:
                logger.error(f"Payment not found for external_id: {external_id}")
                return Response({"error": "Payment not found"}, status=404)
            
            # Store webhook event
            webhook_event = PaymentWebhook.objects.create(
                provider='azampay',
                event_id=transaction_id or f"azam_{external_id}",
                event_type='payment_status_update',
                raw_data=webhook_data,
                payment=payment
            )
            
            # Update payment status based on webhook
            if status_value:
                old_status = payment.status
                
                # Map Azam Pay status to our payment status
                status_mapping = {
                    'success': 'completed',
                    'successful': 'completed',
                    'completed': 'completed',
                    'failed': 'failed',
                    'pending': 'processing',
                    'processing': 'processing',
                    'cancelled': 'cancelled',
                    'canceled': 'cancelled',
                }
                
                new_status = status_mapping.get(status_value.lower(), payment.status)
                
                if new_status != old_status:
                    payment.status = new_status
                    
                    if new_status == 'completed':
                        payment.provider_ref = transaction_id
                        payment.processed_at = timezone.now()
                        
                        # Update order status
                        if payment.order:
                            payment.order.status = 'confirmed'
                            payment.order.save()
                    
                    elif new_status == 'failed':
                        payment.failure_reason = webhook_data.get('message', 'Payment failed')
                        payment.failure_code = webhook_data.get('errorCode', 'UNKNOWN')
                    
                    payment.save()
                    
                    logger.info(f"Payment {payment.id} status updated: {old_status} -> {new_status}")
            
            # Mark webhook as processed
            webhook_event.processed = True
            webhook_event.processed_at = timezone.now()
            webhook_event.save()
            
            return Response({"status": "success"}, status=200)
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook data")
            return Response({"error": "Invalid JSON"}, status=400)
        
        except Exception as e:
            logger.error(f"Webhook processing error: {e}")
            return Response({"error": "Internal server error"}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def azam_pay_webhook_simple(request):
    """Simple function-based webhook handler"""
    try:
        webhook_data = json.loads(request.body)
        
        # Log for debugging
        logger.info(f"Azam Pay webhook (simple): {webhook_data}")
        
        # Process webhook (simplified version)
        external_id = webhook_data.get('externalId')
        if external_id:
            try:
                payment = Payment.objects.get(id=external_id)
                status_value = webhook_data.get('status', '').lower()
                
                if status_value in ['success', 'successful', 'completed']:
                    payment.status = 'completed'
                    payment.provider_ref = webhook_data.get('transactionId')
                    payment.save()
                    
                    # Update order
                    if payment.order:
                        payment.order.status = 'confirmed'
                        payment.order.save()
                
            except Payment.DoesNotExist:
                pass
        
        return HttpResponse("OK", status=200)
        
    except Exception as e:
        logger.error(f"Simple webhook error: {e}")
        return HttpResponse("Error", status=500)
