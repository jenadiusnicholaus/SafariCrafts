import django_filters
from django.db import models
from .models import Artwork, Category


class ArtworkFilter(django_filters.FilterSet):
    """Artwork filtering"""
    
    # Price range filtering
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    
    # Category filtering
    category = django_filters.CharFilter(field_name='category__slug', lookup_expr='iexact')
    
    # Text-based filtering
    tribe = django_filters.CharFilter(lookup_expr='icontains')
    region = django_filters.CharFilter(lookup_expr='icontains')
    material = django_filters.CharFilter(lookup_expr='icontains')
    
    # Artist filtering
    artist = django_filters.CharFilter(field_name='artist__display_name', lookup_expr='icontains')
    
    # Status filtering
    is_featured = django_filters.BooleanFilter()
    is_unique = django_filters.BooleanFilter()
    
    # Availability filtering
    available = django_filters.BooleanFilter(method='filter_available')
    
    class Meta:
        model = Artwork
        fields = [
            'price_min', 'price_max', 'category', 'tribe', 'region',
            'material', 'artist', 'is_featured', 'is_unique', 'available'
        ]
    
    def filter_available(self, queryset, name, value):
        """Filter by availability"""
        if value:
            return queryset.filter(stock_quantity__gt=0)
        return queryset
