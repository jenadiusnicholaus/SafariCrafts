from django.contrib import admin
from .models import Artist, Payout


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """Artist admin"""
    
    list_display = ('display_name', 'user', 'tribe', 'region', 'kyc_status', 'is_active', 'created_at')
    list_filter = ('tribe', 'region', 'kyc_status', 'is_active', 'created_at')
    search_fields = ('display_name', 'user__email', 'user__first_name', 'user__last_name', 'bio')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'display_name', 'bio', 'tribe', 'region')
        }),
        ('Online Presence', {
            'fields': ('website', 'instagram', 'facebook', 'twitter')
        }),
        ('Verification & Status', {
            'fields': ('kyc_status', 'id_document', 'id_number', 'is_active')
        }),
        ('Banking Information', {
            'fields': ('bank_name', 'bank_account_number', 'mobile_wallet_number')
        }),
        ('Statistics', {
            'fields': ('total_sales', 'total_artworks', 'average_rating'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('total_sales', 'total_artworks', 'average_rating', 'created_at', 'updated_at')


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    """Payout admin"""
    
    list_display = ('artist', 'amount', 'currency', 'status', 'provider', 'created_at')
    list_filter = ('status', 'provider', 'currency', 'created_at')
    search_fields = ('artist__display_name', 'artist__user__email', 'provider_ref')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Payout Information', {
            'fields': ('artist', 'amount', 'currency', 'provider', 'status')
        }),
        ('Payment Details', {
            'fields': ('provider_ref', 'notes')
        }),
        ('Timestamps', {
            'fields': ('processed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
