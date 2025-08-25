from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from authentication.models import Address
from artists.models import Artist
from catalog.models import Category, Collection, Artwork, Media
from decimal import Decimal
import uuid

User = get_user_model()


class Command(BaseCommand):
    help = 'Load initial test data for SafariCrafts platform'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-users',
            action='store_true',
            help='Skip creating users and only create catalog data',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🎨 Loading SafariCrafts test data...'))
        
        with transaction.atomic():
            if not options['skip_users']:
                self.create_users()
                self.create_artists()
            
            self.create_categories()
            self.create_collections()
            self.create_artworks()
            
        self.stdout.write(self.style.SUCCESS('✅ Test data loaded successfully!'))
        self.print_summary()

    def create_users(self):
        self.stdout.write('👥 Creating users...')
        
        # Create admin user
        admin_user, created = User.objects.get_or_create(
            email='admin@safaricrafts.com',
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'is_verified': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(f'  ✓ Created admin user: {admin_user.email}')

        # Create test buyers
        buyers_data = [
            {
                'email': 'john.buyer@example.com',
                'username': 'johnbuyer',
                'first_name': 'John',
                'last_name': 'Smith',
                'phone': '+255700000001',
                'role': 'buyer',
            },
            {
                'email': 'mary.collector@example.com',
                'username': 'marycollector',
                'first_name': 'Mary',
                'last_name': 'Johnson',
                'phone': '+255700000002',
                'role': 'buyer',
            }
        ]

        for buyer_data in buyers_data:
            buyer, created = User.objects.get_or_create(
                email=buyer_data['email'],
                defaults=buyer_data
            )
            if created:
                buyer.set_password('password123')
                buyer.save()
                self.stdout.write(f'  ✓ Created buyer: {buyer.email}')

                # Create address for buyer
                Address.objects.create(
                    user=buyer,
                    type='shipping',
                    line1='123 Uhuru Street',
                    city='Dar es Salaam',
                    state='Dar es Salaam',
                    postal_code='12345',
                    country='Tanzania',
                    is_default=True
                )

        # Create test artists
        artists_data = [
            {
                'email': 'maria.makonde@example.com',
                'username': 'mariamakonde',
                'first_name': 'Maria',
                'last_name': 'Makonde',
                'phone': '+255700000003',
                'role': 'artist',
            },
            {
                'email': 'joseph.tingatinga@example.com',
                'username': 'josephtinga',
                'first_name': 'Joseph',
                'last_name': 'Tinga',
                'phone': '+255700000004',
                'role': 'artist',
            },
            {
                'email': 'fatuma.maasai@example.com',
                'username': 'fatumamaasai',
                'first_name': 'Fatuma',
                'last_name': 'Maasai',
                'phone': '+255700000005',
                'role': 'artist',
            }
        ]

        for artist_data in artists_data:
            artist_user, created = User.objects.get_or_create(
                email=artist_data['email'],
                defaults=artist_data
            )
            if created:
                artist_user.set_password('password123')
                artist_user.save()
                self.stdout.write(f'  ✓ Created artist user: {artist_user.email}')

    def create_artists(self):
        self.stdout.write('🎭 Creating artist profiles...')
        
        artist_profiles_data = [
            {
                'user_email': 'maria.makonde@example.com',
                'display_name': 'Maria Makonde',
                'bio': 'Master carver from the Makonde tribe, specializing in traditional Ujamaa sculptures and contemporary interpretations of ancestral spirits.',
                'tribe': 'Makonde',
                'region': 'Mtwara',
                'website': 'https://mariamakonde.art',
                'instagram': '@maria_makonde_art',
                'kyc_status': 'approved',
            },
            {
                'user_email': 'joseph.tingatinga@example.com',
                'display_name': 'Joseph Tinga',
                'bio': 'Contemporary Tinga Tinga painter inspired by the legendary Edward Said Tingatinga. Specializes in vibrant wildlife and cultural scenes.',
                'tribe': 'Makua',
                'region': 'Dar es Salaam',
                'website': 'https://josephtinga.com',
                'instagram': '@joseph_tingatinga',
                'kyc_status': 'approved',
            },
            {
                'user_email': 'fatuma.maasai@example.com',
                'display_name': 'Fatuma Maasai',
                'bio': 'Traditional Maasai beadwork artist creating authentic jewelry and ceremonial pieces using techniques passed down through generations.',
                'tribe': 'Maasai',
                'region': 'Arusha',
                'instagram': '@fatuma_maasai_beads',
                'kyc_status': 'approved',
            }
        ]

        for profile_data in artist_profiles_data:
            try:
                user = User.objects.get(email=profile_data['user_email'])
                artist, created = Artist.objects.get_or_create(
                    user=user,
                    defaults={
                        'display_name': profile_data['display_name'],
                        'bio': profile_data['bio'],
                        'tribe': profile_data['tribe'],
                        'region': profile_data['region'],
                        'website': profile_data.get('website', ''),
                        'instagram': profile_data.get('instagram', ''),
                        'kyc_status': profile_data['kyc_status'],
                    }
                )
                if created:
                    self.stdout.write(f'  ✓ Created artist profile: {artist.display_name}')
            except User.DoesNotExist:
                self.stdout.write(f'  ⚠️  User not found: {profile_data["user_email"]}')

    def create_categories(self):
        self.stdout.write('📂 Creating categories...')
        
        categories_data = [
            {
                'name': 'Sculptures',
                'description': 'Traditional and contemporary sculptures including wood carvings and stone work'
            },
            {
                'name': 'Paintings',
                'description': 'Tinga Tinga paintings, contemporary art, and traditional artwork'
            },
            {
                'name': 'Jewelry',
                'description': 'Traditional Maasai beadwork, silver jewelry, and contemporary pieces'
            },
            {
                'name': 'Textiles',
                'description': 'Kanga, Kitenge fabrics, and traditional woven materials'
            },
            {
                'name': 'Pottery',
                'description': 'Traditional ceramics and contemporary pottery'
            }
        ]

        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created category: {category.name}')

    def create_collections(self):
        self.stdout.write('📚 Creating collections...')
        
        collections_data = [
            {
                'title': 'Makonde Masterpieces',
                'description': 'Exquisite traditional and contemporary Makonde sculptures representing the rich cultural heritage of the Makonde people.',
                'is_featured': True,
            },
            {
                'title': 'Tinga Tinga Classics',
                'description': 'Vibrant Tinga Tinga paintings featuring African wildlife and cultural scenes in the iconic style.',
                'is_featured': True,
            },
            {
                'title': 'Maasai Heritage',
                'description': 'Authentic Maasai jewelry, beadwork, and ceremonial pieces crafted using traditional techniques.',
                'is_featured': False,
            },
            {
                'title': 'Contemporary Africa',
                'description': 'Modern interpretations of traditional African art by contemporary artists.',
                'is_featured': False,
            }
        ]

        for coll_data in collections_data:
            collection, created = Collection.objects.get_or_create(
                title=coll_data['title'],
                defaults={
                    'description': coll_data['description'],
                    'is_featured': coll_data['is_featured'],
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created collection: {collection.title}')

    def create_artworks(self):
        self.stdout.write('🎨 Creating artworks...')
        
        # Get categories and collections
        sculpture_cat = Category.objects.get(name='Sculptures')
        painting_cat = Category.objects.get(name='Paintings')
        jewelry_cat = Category.objects.get(name='Jewelry')
        
        makonde_coll = Collection.objects.get(title='Makonde Masterpieces')
        tinga_coll = Collection.objects.get(title='Tinga Tinga Classics')
        maasai_coll = Collection.objects.get(title='Maasai Heritage')
        
        # Get artists
        try:
            maria_artist = Artist.objects.get(user__email='maria.makonde@example.com')
            joseph_artist = Artist.objects.get(user__email='joseph.tingatinga@example.com')
            fatuma_artist = Artist.objects.get(user__email='fatuma.maasai@example.com')
        except Artist.DoesNotExist:
            self.stdout.write('  ⚠️  Some artists not found, creating artworks with first available artist')
            artists = Artist.objects.all()
            if not artists.exists():
                self.stdout.write('  ❌ No artists found, skipping artwork creation')
                return
            maria_artist = joseph_artist = fatuma_artist = artists.first()

        artworks_data = [
            # Maria's Makonde Sculptures
            {
                'artist': maria_artist,
                'title': 'Ujamaa Unity Tree',
                'description': 'A traditional Ujamaa sculpture representing family unity and community bonds. Hand-carved from African blackwood (Mpingo) with intricate details showing interconnected figures.',
                'story': 'This piece was inspired by the Makonde concept of Ujamaa - family unity. The intertwined figures represent how families support each other through generations.',
                'meaning': 'In Makonde culture, the Unity Tree symbolizes the strength that comes from community. Each figure represents a family member, and together they form an unbreakable bond.',
                'category': sculpture_cat,
                'collections': [makonde_coll],
                'tribe': 'Makonde',
                'region': 'Mtwara',
                'material': 'African Blackwood (Mpingo)',
                'dimensions': '45 x 30 x 25 cm',
                'weight': Decimal('2.5'),
                'price': Decimal('850000'),  # TZS
                'currency': 'TZS',
                'tags': ['traditional', 'ujamaa', 'family', 'sculpture', 'handcarved'],
                'is_featured': True,
                'status': 'active',
            },
            {
                'artist': maria_artist,
                'title': 'Spirit Ancestor Mask',
                'description': 'Contemporary interpretation of traditional Makonde spirit masks, carved with modern artistic flair while respecting ancestral traditions.',
                'story': 'This mask represents the spirits of our ancestors who guide and protect us. Each line and curve tells a story of wisdom passed down through generations.',
                'meaning': 'The mask serves as a bridge between the living and the ancestral spirits, used in ceremonies to honor those who came before us.',
                'category': sculpture_cat,
                'collections': [makonde_coll],
                'tribe': 'Makonde',
                'region': 'Mtwara',
                'material': 'Ebony Wood',
                'dimensions': '35 x 25 x 15 cm',
                'weight': Decimal('1.8'),
                'price': Decimal('450000'),
                'currency': 'TZS',
                'tags': ['mask', 'spiritual', 'ancestor', 'ceremony', 'ebony'],
                'is_featured': False,
                'status': 'active',
            },
            
            # Joseph's Tinga Tinga Paintings
            {
                'artist': joseph_artist,
                'title': 'Serengeti Migration',
                'description': 'Vibrant Tinga Tinga painting depicting the great wildebeest migration across the Serengeti plains, painted in traditional enamel paints.',
                'story': 'Every year, millions of wildebeest cross the Serengeti in search of fresh grass. This painting captures the movement and energy of this incredible natural phenomenon.',
                'meaning': 'The migration represents the cycle of life, renewal, and the harmony between animals and nature.',
                'category': painting_cat,
                'collections': [tinga_coll],
                'tribe': 'Makua',
                'region': 'Dar es Salaam',
                'material': 'Enamel paint on canvas',
                'dimensions': '60 x 80 cm',
                'weight': Decimal('1.2'),
                'price': Decimal('320000'),
                'currency': 'TZS',
                'tags': ['tingatinga', 'wildlife', 'serengeti', 'migration', 'colorful'],
                'is_featured': True,
                'status': 'active',
            },
            {
                'artist': joseph_artist,
                'title': 'Baobab Sunset',
                'description': 'A stunning Tinga Tinga painting featuring the iconic baobab tree silhouetted against a vibrant African sunset with local wildlife.',
                'story': 'The baobab tree is known as the Tree of Life in Africa. This painting shows how all creatures gather around it for shelter and sustenance.',
                'meaning': 'The baobab represents wisdom, longevity, and the center of community life in African villages.',
                'category': painting_cat,
                'collections': [tinga_coll],
                'tribe': 'Makua',
                'region': 'Dar es Salaam',
                'material': 'Enamel paint on canvas',
                'dimensions': '50 x 70 cm',
                'weight': Decimal('0.9'),
                'price': Decimal('280000'),
                'currency': 'TZS',
                'tags': ['tingatinga', 'baobab', 'sunset', 'tree of life', 'african'],
                'is_featured': False,
                'status': 'active',
            },
            
            # Fatuma's Maasai Jewelry
            {
                'artist': fatuma_artist,
                'title': 'Maasai Warrior Necklace',
                'description': 'Traditional Maasai beaded necklace worn by warriors, featuring authentic patterns in red, blue, and white beads with geometric designs.',
                'story': 'This necklace was crafted using the same techniques my grandmother taught me. Each color and pattern has special meaning in Maasai culture.',
                'meaning': 'Red represents bravery and strength, blue represents energy and the sky, white represents peace and purity.',
                'category': jewelry_cat,
                'collections': [maasai_coll],
                'tribe': 'Maasai',
                'region': 'Arusha',
                'material': 'Glass beads, brass wire',
                'dimensions': 'Diameter: 25 cm',
                'weight': Decimal('0.3'),
                'price': Decimal('75000'),
                'currency': 'TZS',
                'tags': ['maasai', 'beadwork', 'necklace', 'warrior', 'traditional'],
                'is_featured': True,
                'status': 'active',
            },
            {
                'artist': fatuma_artist,
                'title': 'Ceremonial Bracelet Set',
                'description': 'Set of three traditional Maasai bracelets worn during important ceremonies and celebrations, featuring intricate beadwork patterns.',
                'story': 'These bracelets are worn during coming-of-age ceremonies and wedding celebrations. Each pattern tells the story of the wearer.',
                'meaning': 'The patterns represent different stages of life and the journey from childhood to adulthood in Maasai society.',
                'category': jewelry_cat,
                'collections': [maasai_coll],
                'tribe': 'Maasai',
                'region': 'Arusha',
                'material': 'Glass beads, leather, brass',
                'dimensions': 'Each bracelet: 20 cm circumference',
                'weight': Decimal('0.2'),
                'price': Decimal('120000'),
                'currency': 'TZS',
                'tags': ['maasai', 'bracelet', 'ceremony', 'celebration', 'set'],
                'is_featured': False,
                'status': 'active',
            }
        ]

        for artwork_data in artworks_data:
            collections = artwork_data.pop('collections', [])
            artwork, created = Artwork.objects.get_or_create(
                title=artwork_data['title'],
                artist=artwork_data['artist'],
                defaults=artwork_data
            )
            
            if created:
                # Add to collections
                for collection in collections:
                    artwork.collections.add(collection)
                
                self.stdout.write(f'  ✓ Created artwork: {artwork.title} by {artwork.artist.display_name}')

    def print_summary(self):
        self.stdout.write('\n📊 DATABASE SUMMARY:')
        self.stdout.write(f'👥 Users: {User.objects.count()}')
        self.stdout.write(f'🎭 Artists: {Artist.objects.count()}')
        self.stdout.write(f'📂 Categories: {Category.objects.count()}')
        self.stdout.write(f'📚 Collections: {Collection.objects.count()}')
        self.stdout.write(f'🎨 Artworks: {Artwork.objects.count()}')
        self.stdout.write(f'📍 Addresses: {Address.objects.count()}')
        
        self.stdout.write('\n🔑 TEST CREDENTIALS:')
        self.stdout.write('Admin: admin@safaricrafts.com / admin123')
        self.stdout.write('Artist: maria.makonde@example.com / password123')
        self.stdout.write('Artist: joseph.tingatinga@example.com / password123')
        self.stdout.write('Artist: fatuma.maasai@example.com / password123')
        self.stdout.write('Buyer: john.buyer@example.com / password123')
        self.stdout.write('Buyer: mary.collector@example.com / password123')
        
        self.stdout.write('\n🚀 Next steps:')
        self.stdout.write('1. Visit http://localhost:8000/admin/ to manage content')
        self.stdout.write('2. Visit http://localhost:8000/api/docs/ for API documentation')
        self.stdout.write('3. Test the API endpoints with the created data')
        self.stdout.write('4. Run: python demo_api.py to test the API')
