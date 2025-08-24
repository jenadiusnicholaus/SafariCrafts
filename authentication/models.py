from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model for SafariCrafts"""
    
    BUYER = 'buyer'
    ARTIST = 'artist'
    ADMIN = 'admin'
    
    ROLE_CHOICES = [
        (BUYER, _('Buyer')),
        (ARTIST, _('Artist')),
        (ADMIN, _('Admin')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    phone = models.CharField(_('phone number'), max_length=20, blank=True)
    role = models.CharField(
        _('role'),
        max_length=10,
        choices=ROLE_CHOICES,
        default=BUYER
    )
    locale = models.CharField(_('locale'), max_length=10, default='en')
    is_verified = models.BooleanField(_('is verified'), default=False)
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Address(models.Model):
    """Address model for users"""
    
    BILLING = 'billing'
    SHIPPING = 'shipping'
    
    TYPE_CHOICES = [
        (BILLING, _('Billing Address')),
        (SHIPPING, _('Shipping Address')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(_('address type'), max_length=10, choices=TYPE_CHOICES)
    line1 = models.CharField(_('address line 1'), max_length=255)
    line2 = models.CharField(_('address line 2'), max_length=255, blank=True)
    city = models.CharField(_('city'), max_length=100)
    state = models.CharField(_('state/region'), max_length=100)
    postal_code = models.CharField(_('postal code'), max_length=20)
    country = models.CharField(_('country'), max_length=100)
    latitude = models.DecimalField(_('latitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(_('longitude'), max_digits=9, decimal_places=6, blank=True, null=True)
    is_default = models.BooleanField(_('is default'), default=False)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'user_addresses'
        verbose_name = _('Address')
        verbose_name_plural = _('Addresses')
        unique_together = ['user', 'type', 'is_default']
    
    def __str__(self):
        return f"{self.line1}, {self.city}, {self.country} ({self.get_type_display()})"
