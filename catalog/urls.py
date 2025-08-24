from django.urls import path
from .views import (
    CategoryListView, CollectionListView, CollectionDetailView,
    ArtworkListView, ArtworkDetailView, ArtworkCreateView, ArtworkUpdateView,
    CartView, CartItemView, artwork_stats, filter_options
)

app_name = 'catalog'

urlpatterns = [
    # Categories
    path('categories/', CategoryListView.as_view(), name='category_list'),
    
    # Collections
    path('collections/', CollectionListView.as_view(), name='collection_list'),
    path('collections/<slug:slug>/', CollectionDetailView.as_view(), name='collection_detail'),
    
    # Artworks
    path('artworks/', ArtworkListView.as_view(), name='artwork_list'),
    path('artworks/create/', ArtworkCreateView.as_view(), name='artwork_create'),
    path('artworks/<slug:slug>/', ArtworkDetailView.as_view(), name='artwork_detail'),
    path('artworks/<int:pk>/update/', ArtworkUpdateView.as_view(), name='artwork_update'),
    
    # Cart
    path('cart/', CartView.as_view(), name='cart'),
    path('cart/items/', CartItemView.as_view(), name='cart_add_item'),
    path('cart/items/<int:item_id>/', CartItemView.as_view(), name='cart_item_detail'),
    
    # Stats and Filters
    path('stats/', artwork_stats, name='artwork_stats'),
    path('filter-options/', filter_options, name='filter_options'),
]
