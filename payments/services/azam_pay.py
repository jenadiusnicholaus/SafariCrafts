import json
import requests
import logging
from django.conf import settings
from django.utils import timezone
from authentication.models import AzamPayAuthToken
from authentication.serializers import AzamPayAuthSerializer

logger = logging.getLogger(__name__)


class AzamPayAuth:
    """Azam Pay Authentication Service"""
    
    def __init__(self):
        self.client_id = settings.AZAM_PAY_CLIENT_ID
        self.client_secret = settings.AZAM_PAY_CLIENT_SECRET
        self.app_name = settings.AZAM_PAY_APP_NAME
        self.auth_url = settings.AZAM_PAY_AUTH
    
    def get_token(self):
        """Get valid authentication token"""
        try:
            # Check if we have a valid token
            token_model = AzamPayAuthToken.objects.latest("created_at")
            if token_model and not token_model.is_expired:
                return token_model.access_token.strip()
        except AzamPayAuthToken.DoesNotExist:
            pass
        
        # Get new token
        return self._request_new_token()
    
    def _request_new_token(self):
        """Request new token from Azam Pay"""
        url = f"{self.auth_url}/AppRegistration/GenerateToken"
        
        payload = {
            "appName": self.app_name,
            "clientId": self.client_id,
            "clientSecret": self.client_secret,
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            response_data = response.json()
            
            if response_data.get("success"):
                token_data = response_data["data"]
                
                # Save token to database
                serializer_data = {
                    'access_token': token_data.get("accessToken"),
                    'refresh_token': token_data.get("refreshToken", ""),
                    'token_type': token_data.get("tokenType", "Bearer"),
                    'expires_in': token_data.get("expire"),
                }
                
                serializer = AzamPayAuthSerializer(data=serializer_data)
                if serializer.is_valid():
                    token_instance = serializer.save()
                    return token_instance.access_token.strip()
                else:
                    logger.error(f"Token serialization error: {serializer.errors}")
                    raise Exception("Failed to save authentication token")
            else:
                logger.error(f"Azam Pay auth failed: {response_data}")
                raise Exception("Authentication failed")
                
        except requests.RequestException as e:
            logger.error(f"Azam Pay auth request failed: {e}")
            raise Exception("Failed to authenticate with Azam Pay")


class AzamPayCheckout:
    """Azam Pay Checkout Service"""
    
    def __init__(self):
        self.checkout_url = settings.AZAM_PAY_CHECKOUT_URL
        self.auth_service = AzamPayAuth()
    
    def init_checkout(self, account_number, amount, external_id, provider="Airtel"):
        """Initialize checkout with Azam Pay"""
        token = self.auth_service.get_token()
        
        url = f"{self.checkout_url}/azampay/mno/checkout"
        
        payload = {
            "accountNumber": account_number,
            "additionalProperties": {"property1": None, "property2": None},
            "amount": str(amount),
            "currency": "TZS",
            "externalId": external_id,
            "provider": provider,
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Azam Pay checkout failed: {e}")
            raise Exception("Failed to initialize payment")
    
    def check_payment_status(self, transaction_id):
        """Check payment status"""
        # Implementation depends on Azam Pay's status check endpoint
        # This is a placeholder - update with actual Azam Pay status endpoint
        token = self.auth_service.get_token()
        
        # Add actual status check implementation here
        pass
    
    def process_mobile_payment(self, phone_number, amount, external_id, provider="Airtel"):
        """Process mobile money payment"""
        # Normalize phone number
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        elif phone_number.startswith('0'):
            phone_number = '255' + phone_number[1:]
        
        # Map provider names to Azam Pay format
        provider_mapping = {
            'mpesa': 'Vodacom',
            'airtel_money': 'Airtel',
            'tigo_pesa': 'Tigo',
        }
        
        azam_provider = provider_mapping.get(provider.lower(), provider)
        
        return self.init_checkout(
            account_number=phone_number,
            amount=amount,
            external_id=external_id,
            provider=azam_provider
        )


class AzamPayService:
    """Main Azam Pay service class"""
    
    def __init__(self):
        self.auth = AzamPayAuth()
        self.checkout = AzamPayCheckout()
    
    def process_payment(self, payment_data):
        """Process payment through Azam Pay"""
        method = payment_data.get('method')
        
        if method in ['mpesa', 'airtel_money', 'tigo_pesa']:
            return self.checkout.process_mobile_payment(
                phone_number=payment_data.get('phone_number'),
                amount=payment_data.get('amount'),
                external_id=payment_data.get('external_id'),
                provider=method
            )
        elif method == 'bank_transfer':
            # Handle bank transfer
            return self.checkout.init_checkout(
                account_number=payment_data.get('account_number'),
                amount=payment_data.get('amount'),
                external_id=payment_data.get('external_id'),
                provider='Bank'
            )
        else:
            raise ValueError(f"Unsupported payment method: {method}")
