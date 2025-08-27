from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class Category(models.Model):
    """Artwork category model"""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'), blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='children'
    )
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    class Meta:
        db_table = 'categories'
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['sort_order', 'name']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Collection(models.Model):
    """Curated collection model"""
    
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True)
    description = models.TextField(_('description'))
    cover_image = models.ImageField(_('cover image'), upload_to='collections/', blank=True, null=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    is_active = models.BooleanField(_('is active'), default=True)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'collections'
        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')
        ordering = ['sort_order', 'title']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title


class Artwork(models.Model):
    """Main artwork model"""
    
    DRAFT = 'draft'
    PENDING = 'pending'
    ACTIVE = 'active'
    SOLD = 'sold'
    INACTIVE = 'inactive'
    REJECTED = 'rejected'
    
    STATUS_CHOICES = [
        (DRAFT, _('Draft')),
        (PENDING, _('Pending Review')),
        (ACTIVE, _('Active')),
        (SOLD, _('Sold')),
        (INACTIVE, _('Inactive')),
        (REJECTED, _('Rejected')),
    ]
    
    # Basic Information
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    artist = models.ForeignKey('artists.Artist', on_delete=models.CASCADE, related_name='artworks')
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), unique=True, max_length=250)
    description = models.TextField(_('description'))
    story = models.TextField(_('story'), blank=True, help_text=_('The story behind this artwork'))
    meaning = models.TextField(_('cultural meaning'), blank=True)
    
    # Categorization
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='artworks')
    collections = models.ManyToManyField(Collection, blank=True, related_name='artworks')
    tribe = models.CharField(_('tribe'), max_length=100, blank=True)
    region = models.CharField(_('region'), max_length=100, blank=True)
    material = models.CharField(_('material'), max_length=200)
    tags = models.JSONField(_('tags'), default=list, blank=True)
    
    # Physical Attributes
    dimensions = models.CharField(_('dimensions'), max_length=100, help_text=_('L x W x H in cm'))
    weight = models.DecimalField(_('weight in kg'), max_digits=8, decimal_places=3, null=True, blank=True)
    
    # Pricing and Inventory
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=2)
    currency = models.CharField(_('currency'), max_length=3, default='TZS')
    stock_quantity = models.PositiveIntegerField(_('stock quantity'), default=1)
    
    # Status and Metadata
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default=DRAFT)
    is_featured = models.BooleanField(_('is featured'), default=False)
    is_unique = models.BooleanField(_('is unique piece'), default=True)
    
    # Flexible attributes for varying artwork types
    attributes = models.JSONField(_('attributes'), default=dict, blank=True)
    
    # SEO
    meta_description = models.CharField(_('meta description'), max_length=160, blank=True)
    meta_keywords = models.CharField(_('meta keywords'), max_length=255, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    
    # Stats
    view_count = models.PositiveIntegerField(_('view count'), default=0)
    like_count = models.PositiveIntegerField(_('like count'), default=0)
    likes = models.ManyToManyField(
        User,
        related_name='liked_artworks',
        blank=True,
        verbose_name=_('likes')
    )
    
    class Meta:
        db_table = 'artworks'
        verbose_name = _('Artwork')
        verbose_name_plural = _('Artworks')
        indexes = [
            models.Index(fields=['artist', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['tribe', 'region']),
            models.Index(fields=['price', 'currency']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_featured', 'status']),
        ]
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.artist.display_name}")
            self.slug = base_slug
            counter = 1
            while Artwork.objects.filter(slug=self.slug).exists():
                self.slug = f"{base_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.title} by {self.artist.display_name}"
    
    @property
    def is_available(self):
        return self.status == self.ACTIVE and self.stock_quantity > 0
    
    @property
    def main_image(self):
        return self.media.filter(kind='image', is_primary=True).first()
    
    @property
    def price_in_usd(self):
        # Simplified conversion - in production, use real exchange rates
        if self.currency == 'USD':
            return self.price
        elif self.currency == 'TZS':
            return self.price / 2300  # Approximate rate
        return self.price


class Media(models.Model):
    """Media files for artworks"""
    
    IMAGE = 'image'
    VIDEO = 'video'
    GLB = 'glb'  # 3D model for web
    USDZ = 'usdz'  # 3D model for iOS AR
    
    KIND_CHOICES = [
        (IMAGE, _('Image')),
        (VIDEO, _('Video')),
        (GLB, _('3D Model (GLB)')),
        (USDZ, _('3D Model (USDZ)')),
    ]
    
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE, related_name='media')
    kind = models.CharField(_('kind'), max_length=10, choices=KIND_CHOICES)
    file = models.FileField(_('file'), upload_to='artwork_media/')
    thumbnail = models.ImageField(_('thumbnail'), upload_to='artwork_thumbnails/', blank=True, null=True)
    
    alt_text = models.CharField(_('alt text'), max_length=200, blank=True)
    caption = models.CharField(_('caption'), max_length=500, blank=True)
    
    is_primary = models.BooleanField(_('is primary'), default=False)
    sort_order = models.PositiveIntegerField(_('sort order'), default=0)
    
    # Metadata
    file_size = models.PositiveIntegerField(_('file size'), null=True, blank=True)
    width = models.PositiveIntegerField(_('width'), null=True, blank=True)
    height = models.PositiveIntegerField(_('height'), null=True, blank=True)
    duration = models.DurationField(_('duration'), null=True, blank=True)  # For videos
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'artwork_media'
        verbose_name = _('Media')
        verbose_name_plural = _('Media')
        ordering = ['sort_order', 'created_at']
        indexes = [
            models.Index(fields=['artwork', 'kind']),
            models.Index(fields=['is_primary']),
        ]
    
    def __str__(self):
        return f"{self.artwork.title} - {self.get_kind_display()}"


class Cart(models.Model):
    """Shopping cart model"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    currency = models.CharField(_('currency'), max_length=3, default='TZS')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'carts'
        verbose_name = _('Cart')
        verbose_name_plural = _('Carts')
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())
    
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """Cart item model"""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    artwork = models.ForeignKey(Artwork, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(_('quantity'), default=1)
    unit_price = models.DecimalField(_('unit price'), max_digits=10, decimal_places=2)
    
    # Snapshot of artwork data at time of adding to cart
    snapshot = models.JSONField(_('artwork snapshot'), default=dict)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        verbose_name = _('Cart Item')
        verbose_name_plural = _('Cart Items')
        unique_together = ['cart', 'artwork']
    
    def __str__(self):
        return f"{self.artwork.title} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.artwork.price
        
        # Save artwork snapshot
        self.snapshot = {
            'title': self.artwork.title,
            'artist': self.artwork.artist.display_name,
            'price': str(self.artwork.price),
            'currency': self.artwork.currency,
            'image_url': self.artwork.main_image.file.url if self.artwork.main_image else None,
        }
        
        super().save(*args, **kwargs)
