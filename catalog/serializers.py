from rest_framework import serializers
from django.db import transaction
from .models import Category, Collection, Artwork, Media, Cart, CartItem


class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description', 'parent', 'children', 'is_active', 'sort_order')
        read_only_fields = ('id', 'slug')
    
    def get_children(self, obj):
        if obj.children.exists():
            return CategorySerializer(obj.children.filter(is_active=True), many=True).data
        return []


class MediaSerializer(serializers.ModelSerializer):
    """Media serializer"""
    
    class Meta:
        model = Media
        fields = (
            'id', 'kind', 'file', 'thumbnail', 'alt_text', 'caption',
            'is_primary', 'sort_order', 'file_size', 'width', 'height',
            'duration', 'created_at'
        )
        read_only_fields = ('id', 'file_size', 'width', 'height', 'created_at')


class ArtworkListSerializer(serializers.ModelSerializer):
    """Artwork list serializer (minimal data)"""
    
    artist_name = serializers.CharField(source='artist.display_name', read_only=True)
    main_image = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'slug', 'artist_name', 'category_name',
            'price', 'currency', 'main_image', 'is_featured',
            'tribe', 'region', 'material', 'view_count', 'like_count'
        )
    
    def get_main_image(self, obj):
        main_media = obj.media.filter(kind='image', is_primary=True).first()
        if main_media:
            return MediaSerializer(main_media).data
        # Fallback to first image
        first_image = obj.media.filter(kind='image').first()
        if first_image:
            return MediaSerializer(first_image).data
        return None


class ArtworkDetailSerializer(serializers.ModelSerializer):
    """Artwork detail serializer (full data)"""
    
    artist = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    collections = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'slug', 'description', 'story', 'meaning',
            'artist', 'category', 'collections', 'tribe', 'region',
            'material', 'tags', 'dimensions', 'weight', 'price',
            'currency', 'stock_quantity', 'status', 'is_featured',
            'is_unique', 'attributes', 'meta_description',
            'meta_keywords', 'media', 'created_at', 'updated_at',
            'published_at', 'view_count', 'like_count', 'is_available'
        )
    
    def get_artist(self, obj):
        from artists.serializers import ArtistPublicSerializer
        return ArtistPublicSerializer(obj.artist).data


class ArtworkCreateUpdateSerializer(serializers.ModelSerializer):
    """Artwork create/update serializer"""
    
    class Meta:
        model = Artwork
        fields = (
            'title', 'description', 'story', 'meaning', 'category',
            'collections', 'tribe', 'region', 'material', 'tags',
            'dimensions', 'weight', 'price', 'currency', 'stock_quantity',
            'is_unique', 'attributes', 'meta_description', 'meta_keywords'
        )
    
    def create(self, validated_data):
        collections = validated_data.pop('collections', [])
        validated_data['artist'] = self.context['request'].user.artist_profile
        
        with transaction.atomic():
            artwork = Artwork.objects.create(**validated_data)
            if collections:
                artwork.collections.set(collections)
        
        return artwork


class CollectionSerializer(serializers.ModelSerializer):
    """Collection serializer"""
    
    artworks_count = serializers.SerializerMethodField()
    featured_artworks = serializers.SerializerMethodField()
    
    class Meta:
        model = Collection
        fields = (
            'id', 'title', 'slug', 'description', 'cover_image',
            'is_featured', 'is_active', 'sort_order', 'artworks_count',
            'featured_artworks', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')
    
    def get_artworks_count(self, obj):
        return obj.artworks.filter(status='active').count()
    
    def get_featured_artworks(self, obj):
        featured = obj.artworks.filter(status='active')[:4]
        return ArtworkListSerializer(featured, many=True).data


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    
    artwork = ArtworkListSerializer(read_only=True)
    artwork_id = serializers.UUIDField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'artwork', 'artwork_id', 'quantity', 'unit_price',
            'total_price', 'snapshot', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'unit_price', 'snapshot', 'created_at', 'updated_at')
    
    def validate_artwork_id(self, value):
        try:
            artwork = Artwork.objects.get(id=value, status='active')
            if not artwork.is_available:
                raise serializers.ValidationError("This artwork is not available")
            return value
        except Artwork.DoesNotExist:
            raise serializers.ValidationError("Artwork not found or not available")
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def create(self, validated_data):
        cart = self.context['cart']
        artwork_id = validated_data.pop('artwork_id')
        artwork = Artwork.objects.get(id=artwork_id)
        
        # Check if item already exists in cart
        existing_item = cart.items.filter(artwork=artwork).first()
        if existing_item:
            existing_item.quantity += validated_data['quantity']
            existing_item.save()
            return existing_item
        
        validated_data['cart'] = cart
        validated_data['artwork'] = artwork
        return super().create(validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Cart serializer"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_amount = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'currency', 'items', 'total_amount', 'total_items',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ArtworkSearchSerializer(serializers.Serializer):
    """Artwork search parameters serializer"""
    
    query = serializers.CharField(required=False, help_text="Search query")
    category = serializers.CharField(required=False, help_text="Category slug")
    tribe = serializers.CharField(required=False, help_text="Tribe name")
    region = serializers.CharField(required=False, help_text="Region name")
    material = serializers.CharField(required=False, help_text="Material type")
    price_min = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    price_max = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    artist = serializers.CharField(required=False, help_text="Artist display name")
    is_featured = serializers.BooleanField(required=False)
    ordering = serializers.ChoiceField(
        choices=[
            'created_at', '-created_at', 'price', '-price',
            'title', '-title', 'view_count', '-view_count'
        ],
        required=False,
        default='-created_at'
    )
