from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, Address


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar', 'date_of_birth')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Localization'), {
            'fields': ('locale',)
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Address admin"""
    
    list_display = ('user', 'type', 'line1', 'city', 'country', 'is_default', 'created_at')
    list_filter = ('type', 'country', 'is_default', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'line1', 'city')
    ordering = ('-created_at',)
    
    fieldsets = (
        (_('User'), {
            'fields': ('user',)
        }),
        (_('Address Details'), {
            'fields': ('type', 'line1', 'line2', 'city', 'state', 'postal_code', 'country')
        }),
        (_('Coordinates'), {
            'fields': ('latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        (_('Settings'), {
            'fields': ('is_default',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
