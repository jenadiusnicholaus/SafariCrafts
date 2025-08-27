from django.contrib import admin
from .models import Category, Collection, Artwork, Media, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Category admin"""
    
    list_display = ('name', 'parent', 'is_active', 'sort_order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'description')
    ordering = ('sort_order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        ('Settings', {
            'fields': ('is_active', 'sort_order')
        }),
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Collection admin"""
    
    list_display = ('title', 'is_featured', 'is_active', 'created_at')
    list_filter = ('is_featured', 'is_active', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Media', {
            'fields': ('cover_image',)
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_active', 'sort_order')
        }),
    )


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    """Artwork admin"""
    
    list_display = ('title', 'artist', 'category', 'price', 'currency', 'status', 'is_featured', 'created_at')
    list_filter = ('category', 'status', 'currency', 'is_featured', 'tribe', 'region', 'created_at')
    search_fields = ('title', 'description', 'artist__display_name', 'tags')
    ordering = ('-created_at',)
    filter_horizontal = ('collections',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'artist', 'category', 'collections')
        }),
        ('Cultural Context', {
            'fields': ('story', 'meaning', 'tribe', 'region')
        }),
        ('Physical Details', {
            'fields': ('material', 'dimensions', 'weight', 'year_created')
        }),
        ('Pricing & Availability', {
            'fields': ('price', 'currency', 'status', 'quantity_available')
        }),
        ('Classification', {
            'fields': ('tags', 'is_featured')
        }),
        ('SEO', {
            'fields': ('slug',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('slug', 'created_at', 'updated_at')


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    """Media admin"""
    
    list_display = ('artwork', 'kind', 'is_primary', 'sort_order', 'created_at')
    list_filter = ('kind', 'is_primary', 'created_at')
    search_fields = ('artwork__title', 'alt_text', 'caption')
    ordering = ('artwork', 'sort_order')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('artwork', 'kind', 'file', 'thumbnail')
        }),
        ('Display Settings', {
            'fields': ('is_primary', 'sort_order', 'alt_text', 'caption')
        }),
        ('Metadata', {
            'fields': ('file_size', 'width', 'height', 'duration'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Cart admin"""
    
    list_display = ('user', 'total_items', 'total_amount', 'currency', 'created_at', 'updated_at')
    list_filter = ('currency', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    ordering = ('-updated_at',)
    
    readonly_fields = ('total_items', 'total_amount', 'created_at', 'updated_at')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """CartItem admin"""
    
    list_display = ('cart', 'artwork', 'quantity', 'unit_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('cart__user__email', 'artwork__title', 'artwork__artist__display_name')
    ordering = ('-created_at',)
    
    readonly_fields = ('unit_price', 'created_at', 'updated_at')
