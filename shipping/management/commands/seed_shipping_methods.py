from django.core.management.base import BaseCommand
from shipping.models import ShippingMethod

class Command(BaseCommand):
    help = 'Seed the database with default shipping methods for Tanzania.'

    def handle(self, *args, **options):
        methods = [
            {
                'name': 'Standard Delivery',
                'description': 'Regular delivery within Tanzania',
                'carrier': 'DHL',
                'base_cost': 5000.00,
                'cost_per_kg': 2000.00,
                'min_delivery_days': 3,
                'max_delivery_days': 7,
                'max_weight': 30.0,
                'max_dimensions': '60x40x40 cm',
                'domestic_only': True,
                'supported_countries': [],
                'is_active': True,
                'sort_order': 1
            },
            {
                'name': 'Express Delivery',
                'description': 'Fast delivery within Dar es Salaam',
                'carrier': 'Local Courier',
                'base_cost': 8000.00,
                'cost_per_kg': 1000.00,
                'min_delivery_days': 1,
                'max_delivery_days': 2,
                'max_weight': 10.0,
                'max_dimensions': '40x30x30 cm',
                'domestic_only': True,
                'supported_countries': [],
                'is_active': True,
                'sort_order': 2
            },
            {
                'name': 'International Economy',
                'description': 'Economy shipping to select countries',
                'carrier': 'DHL',
                'base_cost': 25000.00,
                'cost_per_kg': 8000.00,
                'min_delivery_days': 7,
                'max_delivery_days': 21,
                'max_weight': 20.0,
                'max_dimensions': '60x40x40 cm',
                'domestic_only': False,
                'supported_countries': ['US', 'GB', 'DE', 'FR', 'IT', 'NL', 'CA', 'AU'],
                'is_active': True,
                'sort_order': 3
            }
        ]

        for method in methods:
            obj, created = ShippingMethod.objects.update_or_create(
                name=method['name'],
                carrier=method['carrier'],
                defaults=method
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {obj}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated: {obj}"))
        self.stdout.write(self.style.SUCCESS('Shipping methods seeding complete.'))
