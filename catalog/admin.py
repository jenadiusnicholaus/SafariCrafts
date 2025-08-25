from django.contrib import admin
from .models import Category, Collection, Artwork, Media, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Collection admin"""
    list_display = ('title', 'is_featured', 'is_active')
    list_filter = ('is_featured', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    """Artwork admin"""
    list_display = ('title', 'artist', 'category', 'price', 'currency', 'status')
    list_filter = ('category', 'status', 'currency')
    search_fields = ('title', 'description', 'artist__display_name')
    ordering = ('-created_at',)
    filter_horizontal = ('collections',)


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Media admin"""
    list_display = ('artwork', 'kind', 'is_primary')
    list_filter = ('kind', 'is_primary')
    search_fields = ('artwork__title',)
    ordering = ('artwork',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin"""
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-updated_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """CartItem admin"""
    list_display = ('cart', 'artwork', 'quantity')
    search_fields = ('cart__user__email', 'artwork__title')
    ordering = ('-created_at',)
