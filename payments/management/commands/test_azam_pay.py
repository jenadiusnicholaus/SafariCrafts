"""
Management command to test Azam Pay integration
"""
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from payments.services.azam_pay import AzamPayAuth, AzamPayService


class Command(BaseCommand):
    help = 'Test Azam Pay integration and authentication'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-auth',
            action='store_true',
            help='Test authentication only',
        )
        parser.add_argument(
            '--test-payment',
            action='store_true',
            help='Test payment processing (requires phone number)',
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number for test payment',
        )
        parser.add_argument(
            '--amount',
            type=float,
            default=1000.0,
            help='Amount for test payment (default: 1000)',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Testing Azam Pay Integration...\n')
        )
        
        # Check configuration
        self.check_configuration()
        
        if options['test_auth']:
            self.test_authentication()
        
        if options['test_payment']:
            if not options['phone']:
                self.stdout.write(
                    self.style.ERROR('❌ Phone number required for payment test. Use --phone +255XXXXXXXXX')
                )
                return
            
            self.test_payment(options['phone'], options['amount'])
    
    def check_configuration(self):
        """Check if Azam Pay is properly configured"""
        self.stdout.write('📋 Checking Azam Pay Configuration...')
        
        required_settings = [
            'AZAM_PAY_CLIENT_ID',
            'AZAM_PAY_CLIENT_SECRET', 
            'AZAM_PAY_APP_NAME',
            'AZAM_PAY_AUTH',
            'AZAM_PAY_CHECKOUT_URL'
        ]
        
        missing_settings = []
        for setting in required_settings:
            value = getattr(settings, setting, None)
            if not value or value.startswith('no_'):
                missing_settings.append(setting)
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  {setting}: Missing or default value')
                )
            else:
                # Mask sensitive data
                if 'SECRET' in setting:
                    display_value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
                else:
                    display_value = value
                self.stdout.write(
                    self.style.SUCCESS(f'   ✅ {setting}: {display_value}')
                )
        
        if missing_settings:
            self.stdout.write(
                self.style.ERROR(f'\n❌ Missing configuration: {", ".join(missing_settings)}')
            )
            self.stdout.write(
                self.style.WARNING('Please update your .env file with proper Azam Pay credentials\n')
            )
            return False
        else:
            self.stdout.write(
                self.style.SUCCESS('✅ All Azam Pay settings configured\n')
            )
            return True
    
    def test_authentication(self):
        """Test Azam Pay authentication"""
        self.stdout.write('🔐 Testing Azam Pay Authentication...')
        
        try:
            auth_service = AzamPayAuth()
            token = auth_service.get_token()
            
            if token:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Authentication successful!')
                )
                self.stdout.write(
                    self.style.SUCCESS(f'   Token: {token[:10]}...{token[-10:]}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Authentication failed - no token received')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Authentication failed: {e}')
            )
    
    def test_payment(self, phone_number, amount):
        """Test payment processing"""
        self.stdout.write(f'💳 Testing Payment Processing...')
        self.stdout.write(f'   Phone: {phone_number}')
        self.stdout.write(f'   Amount: {amount} TZS')
        
        try:
            azam_pay = AzamPayService()
            
            payment_data = {
                'method': 'mpesa',
                'phone_number': phone_number,
                'amount': amount,
                'external_id': f'test_payment_{int(time.time())}'
            }
            
            result = azam_pay.process_payment(payment_data)
            
            if result:
                self.stdout.write(
                    self.style.SUCCESS('✅ Payment request sent successfully!')
                )
                self.stdout.write(f'   Response: {result}')
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Payment request failed')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Payment test failed: {e}')
            )
        
        self.stdout.write(
            self.style.WARNING('\n⚠️  Note: This is a test payment. Check your phone for any payment prompts.')
        )
