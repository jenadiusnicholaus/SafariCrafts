from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Artist(models.Model):
    """Artist profile model"""
    
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    SUSPENDED = 'suspended'
    
    KYC_STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (APPROVED, _('Approved')),
        (REJECTED, _('Rejected')),
        (SUSPENDED, _('Suspended')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    display_name = models.CharField(_('display name'), max_length=100)
    bio = models.TextField(_('biography'), blank=True)
    tribe = models.CharField(_('tribe'), max_length=100, blank=True)
    region = models.CharField(_('region'), max_length=100, blank=True)
    kyc_status = models.CharField(
        _('KYC status'),
        max_length=10,
        choices=KYC_STATUS_CHOICES,
        default=PENDING
    )
    
    # Social media links
    website = models.URLField(_('website'), blank=True)
    instagram = models.CharField(_('Instagram handle'), max_length=100, blank=True)
    facebook = models.CharField(_('Facebook page'), max_length=100, blank=True)
    twitter = models.CharField(_('Twitter handle'), max_length=100, blank=True)
    
    # KYC Documents
    id_document = models.ImageField(_('ID document'), upload_to='kyc/ids/', blank=True, null=True)
    id_number = models.CharField(_('ID number'), max_length=50, blank=True)
    
    # Banking Information
    bank_name = models.CharField(_('bank name'), max_length=100, blank=True)
    bank_account_number = models.CharField(_('bank account number'), max_length=50, blank=True)
    mobile_wallet_number = models.CharField(_('mobile wallet number'), max_length=20, blank=True)
    
    # Stats
    total_sales = models.DecimalField(_('total sales'), max_digits=10, decimal_places=2, default=0)
    total_artworks = models.PositiveIntegerField(_('total artworks'), default=0)
    average_rating = models.DecimalField(_('average rating'), max_digits=3, decimal_places=2, default=0)
    
    is_active = models.BooleanField(_('is active'), default=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'artists'
        verbose_name = _('Artist')
        verbose_name_plural = _('Artists')
        indexes = [
            models.Index(fields=['tribe', 'region']),
            models.Index(fields=['kyc_status']),
        ]
    
    def __str__(self):
        return f"{self.display_name} ({self.user.email})"
    
    @property
    def is_verified(self):
        return self.kyc_status == self.APPROVED
    
    def update_stats(self):
        """Update artist statistics"""
        from catalog.models import Artwork
        from orders.models import OrderItem
        from reviews.models import Review
        
        # Update artwork count
        self.total_artworks = self.artworks.filter(status='active').count()
        
        # Update total sales
        total_sales = OrderItem.objects.filter(
            artwork__artist=self,
            order__status='completed'
        ).aggregate(
            total=models.Sum('unit_price')
        )['total'] or 0
        self.total_sales = total_sales
        
        # Update average rating
        avg_rating = Review.objects.filter(
            artwork__artist=self
        ).aggregate(
            avg=models.Avg('rating')
        )['avg'] or 0
        self.average_rating = round(avg_rating, 2)
        
        self.save()


class Payout(models.Model):
    """Payout model for artist earnings"""
    
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (PROCESSING, _('Processing')),
        (COMPLETED, _('Completed')),
        (FAILED, _('Failed')),
        (CANCELLED, _('Cancelled')),
    ]
    
    BANK_TRANSFER = 'bank_transfer'
    MOBILE_MONEY = 'mobile_money'
    
    PROVIDER_CHOICES = [
        (BANK_TRANSFER, _('Bank Transfer')),
        (MOBILE_MONEY, _('Mobile Money')),
    ]
    
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(_('amount'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='TZS')
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default=PENDING)
    provider = models.CharField(_('provider'), max_length=20, choices=PROVIDER_CHOICES)
    provider_ref = models.CharField(_('provider reference'), max_length=255, blank=True)
    
    # Payout details
    notes = models.TextField(_('notes'), blank=True)
    processed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='processed_payouts'
    )
    processed_at = models.DateTimeField(_('processed at'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'artist_payouts'
        verbose_name = _('Payout')
        verbose_name_plural = _('Payouts')
        indexes = [
            models.Index(fields=['artist', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Payout {self.id} - {self.artist.display_name} - {self.amount} {self.currency}"
