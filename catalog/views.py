from rest_framework import generics, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Min, Max
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from .models import Category, Collection, Artwork, Media, Cart, CartItem
from .serializers import (
    CategorySerializer, CollectionSerializer, ArtworkListSerializer,
    ArtworkDetailSerializer, ArtworkCreateUpdateSerializer, MediaSerializer,
    CartSerializer, CartItemSerializer, ArtworkSearchSerializer
)
from .filters import ArtworkFilter


class CategoryListView(generics.ListCreateAPIView):
    """Category list and create endpoint"""
    
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent=None).order_by('sort_order', 'name')
    
    @extend_schema(
        operation_id='list_categories',
        summary='List categories',
        description='Retrieve all active categories',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='create_category',
        summary='Create category',
        description='Create a new category (admin only)',
    )
    def post(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(
                {'error': 'Only staff can create categories'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().post(request, *args, **kwargs)


class CollectionListView(generics.ListAPIView):
    """Collection list endpoint"""
    
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Collection.objects.filter(is_active=True).order_by('sort_order', 'title')
        if self.request.query_params.get('featured'):
            queryset = queryset.filter(is_featured=True)
        return queryset
    
    @extend_schema(
        operation_id='list_collections',
        summary='List collections',
        description='Retrieve all active collections',
        parameters=[
            OpenApiParameter(
                name='featured',
                description='Filter featured collections only',
                required=False,
                type=bool
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CollectionDetailView(generics.RetrieveAPIView):
    """Collection detail endpoint"""
    
    serializer_class = CollectionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Collection.objects.filter(is_active=True)
    
    @extend_schema(
        operation_id='get_collection',
        summary='Get collection',
        description='Retrieve a specific collection by slug',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ArtworkListView(generics.ListAPIView):
    """Artwork list endpoint with filtering and search"""
    
    serializer_class = ArtworkListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ArtworkFilter
    search_fields = ['title', 'description', 'story', 'artist__display_name', 'tribe', 'region', 'material']
    ordering_fields = ['created_at', 'price', 'title', 'view_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Artwork.objects.filter(status='active').select_related(
            'artist', 'category'
        ).prefetch_related('media', 'collections')
        
        # Collection filtering
        collection_slug = self.request.query_params.get('collection')
        if collection_slug:
            queryset = queryset.filter(collections__slug=collection_slug)
        
        # Featured filtering
        if self.request.query_params.get('featured'):
            queryset = queryset.filter(is_featured=True)
        
        return queryset
    
    @extend_schema(
        operation_id='list_artworks',
        summary='List artworks',
        description='Retrieve artworks with filtering and search capabilities',
        parameters=[
            OpenApiParameter(name='search', description='Search query', required=False, type=str),
            OpenApiParameter(name='category', description='Category slug', required=False, type=str),
            OpenApiParameter(name='collection', description='Collection slug', required=False, type=str),
            OpenApiParameter(name='tribe', description='Tribe name', required=False, type=str),
            OpenApiParameter(name='region', description='Region name', required=False, type=str),
            OpenApiParameter(name='material', description='Material type', required=False, type=str),
            OpenApiParameter(name='price_min', description='Minimum price', required=False, type=float),
            OpenApiParameter(name='price_max', description='Maximum price', required=False, type=float),
            OpenApiParameter(name='featured', description='Featured only', required=False, type=bool),
            OpenApiParameter(name='ordering', description='Ordering', required=False, type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ArtworkDetailView(generics.RetrieveAPIView):
    """Artwork detail endpoint"""
    
    serializer_class = ArtworkDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'
    
    def get_queryset(self):
        return Artwork.objects.filter(status='active').select_related(
            'artist', 'category'
        ).prefetch_related('media', 'collections')
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Increment view count
        Artwork.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @extend_schema(
        operation_id='get_artwork',
        summary='Get artwork',
        description='Retrieve a specific artwork by slug',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ArtworkCreateView(generics.CreateAPIView):
    """Artist artwork creation endpoint"""
    
    serializer_class = ArtworkCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Artwork.objects.filter(artist__user=self.request.user)
    
    def perform_create(self, serializer):
        # Check if user is an artist
        if not hasattr(self.request.user, 'artist_profile'):
            raise permissions.PermissionDenied("Only artists can create artworks")
        
        serializer.save()
    
    @extend_schema(
        operation_id='create_artwork',
        summary='Create artwork',
        description='Create a new artwork (artists only)',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ArtworkUpdateView(generics.RetrieveUpdateAPIView):
    """Artist artwork update endpoint"""
    
    serializer_class = ArtworkCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Artwork.objects.filter(artist__user=self.request.user)
    
    @extend_schema(
        operation_id='update_artwork',
        summary='Update artwork',
        description='Update an existing artwork (owner only)',
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class CartView(APIView):
    """Cart management endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @extend_schema(
        operation_id='get_cart',
        summary='Get cart',
        description='Retrieve current user cart',
        responses={200: CartSerializer}
    )
    def get(self, request):
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data)
    
    @extend_schema(
        operation_id='clear_cart',
        summary='Clear cart',
        description='Remove all items from cart',
    )
    def delete(self, request):
        cart = self.get_cart()
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'})


class CartItemView(APIView):
    """Cart item management endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    @extend_schema(
        operation_id='add_to_cart',
        summary='Add to cart',
        description='Add an artwork to cart',
        request=CartItemSerializer,
        responses={201: CartItemSerializer}
    )
    def post(self, request):
        cart = self.get_cart()
        serializer = CartItemSerializer(data=request.data, context={'cart': cart, 'request': request})
        
        if serializer.is_valid():
            item = serializer.save()
            return Response(CartItemSerializer(item).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id='update_cart_item',
        summary='Update cart item',
        description='Update cart item quantity',
        request=CartItemSerializer,
    )
    def patch(self, request, item_id):
        cart = self.get_cart()
        
        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        operation_id='remove_from_cart',
        summary='Remove from cart',
        description='Remove an item from cart',
    )
    def delete(self, request, item_id):
        cart = self.get_cart()
        
        try:
            item = cart.items.get(id=item_id)
            item.delete()
            return Response({'message': 'Item removed from cart'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@extend_schema(
    operation_id='get_artwork_stats',
    summary='Get artwork statistics',
    description='Get general statistics about artworks',
)
def artwork_stats(request):
    """Get artwork statistics"""
    stats = {
        'total_artworks': Artwork.objects.filter(status='active').count(),
        'total_artists': Artwork.objects.filter(status='active').values('artist').distinct().count(),
        'featured_artworks': Artwork.objects.filter(status='active', is_featured=True).count(),
        'categories': Category.objects.filter(is_active=True).count(),
        'collections': Collection.objects.filter(is_active=True).count(),
    }
    
    return Response(stats)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
@extend_schema(
    operation_id='get_filter_options',
    summary='Get filter options',
    description='Get available filter options for artworks',
)
def filter_options(request):
    """Get available filter options"""
    
    # Get distinct values for filters
    tribes = list(Artwork.objects.filter(status='active').exclude(
        tribe__isnull=True
    ).exclude(tribe='').values_list('tribe', flat=True).distinct())
    
    regions = list(Artwork.objects.filter(status='active').exclude(
        region__isnull=True
    ).exclude(region='').values_list('region', flat=True).distinct())
    
    materials = list(Artwork.objects.filter(status='active').exclude(
        material__isnull=True
    ).exclude(material='').values_list('material', flat=True).distinct())
    
    price_range = Artwork.objects.filter(status='active').aggregate(
        min_price=Min('price'),
        max_price=Max('price')
    )
    
    options = {
        'tribes': sorted(tribes),
        'regions': sorted(regions),
        'materials': sorted(materials),
        'price_range': price_range,
        'categories': CategorySerializer(
            Category.objects.filter(is_active=True),
            many=True
        ).data,
        'collections': [
            {'slug': c.slug, 'title': c.title}
            for c in Collection.objects.filter(is_active=True)
        ]
    }
    
    return Response(options)
