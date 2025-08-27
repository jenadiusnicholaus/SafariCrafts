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
        """Return children categories or empty list"""
        try:
            if obj.children.exists():
                return CategorySerializer(obj.children.filter(is_active=True), many=True, context=self.context).data
            return []
        except:
            return []


class MediaSerializer(serializers.ModelSerializer):
    """Media serializer with absolute URLs"""
    
    file = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = (
            'id', 'kind', 'file', 'thumbnail', 'alt_text', 'caption',
            'is_primary', 'sort_order', 'file_size', 'width', 'height',
            'duration', 'created_at'
        )
        read_only_fields = ('id', 'file_size', 'width', 'height', 'created_at')
    
    def get_file(self, obj):
        """Return absolute URL for file or None"""
        try:
            if obj.file:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.file.url)
                return obj.file.url
            return None
        except:
            return None
    
    def get_thumbnail(self, obj):
        """Return absolute URL for thumbnail or None"""
        try:
            if obj.thumbnail:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.thumbnail.url)
                return obj.thumbnail.url
            return None
        except:
            return None


class ArtworkListSerializer(serializers.ModelSerializer):
    """Artwork list serializer (minimal data)"""
    
    artist_name = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'slug', 'artist_name', 'category_name',
            'price', 'currency', 'main_image', 'is_featured',
            'tribe', 'region', 'material', 'view_count', 'like_count', 'is_liked'
        )
    
    def get_artist_name(self, obj):
        """Return artist display name or empty string"""
        try:
            return obj.artist.display_name if obj.artist else ""
        except:
            return ""
    
    def get_category_name(self, obj):
        """Return category name or empty string"""
        try:
            return obj.category.name if obj.category else ""
        except:
            return ""
    
    def get_is_liked(self, obj):
        """Return whether the current user has liked this artwork"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return obj.likes.filter(id=request.user.id).exists()
            except:
                return False
        return False
    
    def get_main_image(self, obj):
        """Return main image or None if no image exists"""
        main_media = obj.media.filter(kind='image', is_primary=True).first()
        if main_media:
            return MediaSerializer(main_media, context=self.context).data
        # Fallback to first image
        first_image = obj.media.filter(kind='image').first()
        if first_image:
            return MediaSerializer(first_image, context=self.context).data
        # Return None if no images exist
        return None


class ArtworkDetailSerializer(serializers.ModelSerializer):
    """Artwork detail serializer (full data)"""
    
    artist = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    collections = serializers.StringRelatedField(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    
    class Meta:
        model = Artwork
        fields = (
            'id', 'title', 'slug', 'description', 'story', 'meaning',
            'artist', 'category', 'collections', 'tribe', 'region',
            'material', 'tags', 'dimensions', 'weight', 'price',
            'currency', 'stock_quantity', 'status', 'is_featured',
            'is_unique', 'attributes', 'meta_description',
            'meta_keywords', 'media', 'created_at', 'updated_at',
            'published_at', 'view_count', 'like_count', 'is_available', 'is_liked'
        )
    
    def get_artist(self, obj):
        """Return artist data or None if artist doesn't exist"""
        if obj.artist:
            from artists.serializers import ArtistPublicSerializer
            return ArtistPublicSerializer(obj.artist, context=self.context).data
        return None
    
    def get_is_liked(self, obj):
        """Return whether the current user has liked this artwork"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                return obj.likes.filter(id=request.user.id).exists()
            except:
                return False
        return False


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
        """Return count of active artworks or 0"""
        try:
            return obj.artworks.filter(status='active').count()
        except:
            return 0
    
    def get_featured_artworks(self, obj):
        """Return featured artworks or empty list"""
        try:
            featured = obj.artworks.filter(status='active')[:4]
            if featured.exists():
                return ArtworkListSerializer(featured, many=True, context=self.context).data
            return []
        except:
            return []


class CartItemSerializer(serializers.ModelSerializer):
    """Cart item serializer"""
    
    artwork = serializers.SerializerMethodField()
    artwork_id = serializers.UUIDField(write_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = (
            'id', 'artwork', 'artwork_id', 'quantity', 'unit_price',
            'total_price', 'snapshot', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'unit_price', 'snapshot', 'created_at', 'updated_at')
    
    def get_artwork(self, obj):
        """Return artwork data with context for absolute URLs"""
        if obj.artwork:
            return ArtworkListSerializer(obj.artwork, context=self.context).data
        return None
    
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
    
    items = serializers.SerializerMethodField()
    total_amount = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = (
            'id', 'currency', 'items', 'total_amount', 'total_items',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_items(self, obj):
        """Return cart items with context for absolute URLs"""
        items = obj.items.all()
        return CartItemSerializer(items, many=True, context=self.context).data


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
