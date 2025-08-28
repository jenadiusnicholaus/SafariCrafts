"""
Test Azam Pay Integration
"""
from django.test import TestCase
from django.conf import settings
from payments.services.azam_pay import AzamPayAuth, AzamPayCheckout, AzamPayService
from authentication.models import AzamPayAuthToken
from unittest.mock import patch, MagicMock


class AzamPayAuthTest(TestCase):
    """Test Azam Pay Authentication"""
    
    def setUp(self):
        self.auth_service = AzamPayAuth()
    
    @patch('payments.services.azam_pay.requests.post')
    def test_get_new_token(self, mock_post):
        """Test getting new authentication token"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "data": {
                "accessToken": "test_access_token_123",
                "refreshToken": "test_refresh_token_456",
                "tokenType": "Bearer",
                "expire": "1693228800"  # Unix timestamp
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Get token
        token = self.auth_service.get_token()
        
        # Assertions
        self.assertIsNotNone(token)
        self.assertEqual(token, "test_access_token_123")
        
        # Check if token was saved to database
        saved_token = AzamPayAuthToken.objects.latest('created_at')
        self.assertEqual(saved_token.access_token, "test_access_token_123")


class AzamPayCheckoutTest(TestCase):
    """Test Azam Pay Checkout"""
    
    def setUp(self):
        self.checkout_service = AzamPayCheckout()
    
    @patch('payments.services.azam_pay.AzamPayAuth.get_token')
    @patch('payments.services.azam_pay.requests.post')
    def test_mobile_payment(self, mock_post, mock_get_token):
        """Test mobile money payment"""
        # Mock token
        mock_get_token.return_value = "test_token_123"
        
        # Mock checkout response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "success": True,
            "transactionId": "TXN123456789",
            "message": "Payment initiated successfully"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Process payment
        result = self.checkout_service.process_mobile_payment(
            phone_number="+255712345678",
            amount=10000,
            external_id="order_123",
            provider="mpesa"
        )
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertTrue(result.get("success"))
        self.assertEqual(result.get("transactionId"), "TXN123456789")


class AzamPayServiceTest(TestCase):
    """Test main Azam Pay service"""
    
    def setUp(self):
        self.service = AzamPayService()
    
    @patch('payments.services.azam_pay.AzamPayCheckout.process_mobile_payment')
    def test_process_mpesa_payment(self, mock_mobile_payment):
        """Test processing M-Pesa payment"""
        # Mock response
        mock_mobile_payment.return_value = {
            "success": True,
            "transactionId": "MPESA123456"
        }
        
        payment_data = {
            'method': 'mpesa',
            'phone_number': '+255712345678',
            'amount': 50000,
            'external_id': 'order_456'
        }
        
        result = self.service.process_payment(payment_data)
        
        # Assertions
        self.assertIsNotNone(result)
        mock_mobile_payment.assert_called_once()
    
    def test_unsupported_method(self):
        """Test unsupported payment method"""
        payment_data = {
            'method': 'unsupported_method',
            'amount': 10000,
            'external_id': 'order_789'
        }
        
        with self.assertRaises(ValueError):
            self.service.process_payment(payment_data)
