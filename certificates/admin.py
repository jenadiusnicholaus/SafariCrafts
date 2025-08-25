from django.contrib import admin
from .models import Certificate


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Certificate admin"""
    list_display = ('serial_number', 'artwork', 'status')
    list_filter = ('status',)
    search_fields = ('artwork__title', 'artwork__artist__display_name', 'serial_number')
    ordering = ('-created_at',)
