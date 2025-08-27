from django.core.management.base import BaseCommand
from payments.models import PaymentMethod


class Command(BaseCommand):
    help = 'Populate PaymentMethod table with initial payment methods'

    def handle(self, *args, **options):
        payment_methods = [
            {
                "provider": "azampay",
                "method": "mpesa",
                "name": "M-Pesa",
                "description": "Pay with your M-Pesa mobile money",
                "icon_url": "https://example.com/icons/mpesa.png",
                "fee_percentage": 2.5,
                "fixed_fee_amount": 0.00,
                "supported_currencies": ["TZS"],
                "allowed_countries": ["TZ"],
                "is_active": True,
                "sort_order": 1
            },
            {
                "provider": "azampay",
                "method": "airtel_money",
                "name": "Airtel Money", 
                "description": "Pay with your Airtel Money wallet",
                "icon_url": "https://example.com/icons/airtel.png",
                "fee_percentage": 2.5,
                "fixed_fee_amount": 0.00,
                "supported_currencies": ["TZS"],
                "allowed_countries": ["TZ"],
                "is_active": True,
                "sort_order": 2
            },
            {
                "provider": "azampay",
                "method": "tigo_pesa",
                "name": "Tigo Pesa",
                "description": "Pay with your Tigo Pesa wallet",
                "icon_url": "https://example.com/icons/tigo.png",
                "fee_percentage": 2.5,
                "fixed_fee_amount": 0.00,
                "supported_currencies": ["TZS"],
                "allowed_countries": ["TZ"],
                "is_active": True,
                "sort_order": 3
            },
            {
                "provider": "azampay",
                "method": "bank_transfer",
                "name": "Bank Transfer (CRDB & NMB)",
                "description": "Pay directly from your CRDB Bank or NMB Bank account",
                "icon_url": "https://example.com/icons/bank.png",
                "fee_percentage": 1.5,
                "fixed_fee_amount": 0.00,
                "supported_currencies": ["TZS"],
                "allowed_countries": ["TZ"],
                "is_active": True,
                "sort_order": 4,
                "configuration": {
                    "supported_banks": [
                        {"code": "CRDB", "name": "CRDB Bank"},
                        {"code": "NMB", "name": "NMB Bank"}
                    ]
                }
            },
            {
                "provider": "paypal",
                "method": "paypal",
                "name": "PayPal",
                "description": "Pay with your PayPal account (International payments)",
                "icon_url": "https://example.com/icons/paypal.png",
                "fee_percentage": 4.0,
                "fixed_fee_amount": 0.00,
                "supported_currencies": ["USD", "EUR"],
                "allowed_countries": ["US", "CA", "GB", "AU", "DE", "FR", "IT", "ES", "NL"],
                "is_active": True,
                "sort_order": 5
            }
        ]

        for method_data in payment_methods:
            method, created = PaymentMethod.objects.get_or_create(
                provider=method_data['provider'],
                method=method_data['method'],
                defaults=method_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created payment method: {method.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Payment method already exists: {method.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully populated payment methods!')
        )
