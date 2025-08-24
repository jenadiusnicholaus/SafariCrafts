from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Review(models.Model):
    """Product review model"""
    
    # Review identification
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    artwork = models.ForeignKey('catalog.Artwork', on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    
    # Review content
    rating = models.PositiveIntegerField(
        _('rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text=_('Rating from 1 to 5 stars')
    )
    title = models.CharField(_('review title'), max_length=200, blank=True)
    comment = models.TextField(_('comment'), blank=True)
    
    # Review images
    images = models.JSONField(_('review images'), default=list, blank=True)
    
    # Moderation
    is_verified_purchase = models.BooleanField(_('is verified purchase'), default=False)
    is_approved = models.BooleanField(_('is approved'), default=True)
    is_featured = models.BooleanField(_('is featured'), default=False)
    
    # Helpfulness tracking
    helpful_count = models.PositiveIntegerField(_('helpful count'), default=0)
    not_helpful_count = models.PositiveIntegerField(_('not helpful count'), default=0)
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = _('Review')
        verbose_name_plural = _('Reviews')
        ordering = ['-created_at']
        unique_together = ['user', 'artwork']  # One review per user per artwork
        indexes = [
            models.Index(fields=['artwork', 'is_approved']),
            models.Index(fields=['rating']),
            models.Index(fields=['is_verified_purchase']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Review by {self.user.email} for {self.artwork.title} - {self.rating} stars"
    
    @property
    def helpfulness_ratio(self):
        """Calculate helpfulness ratio"""
        total_votes = self.helpful_count + self.not_helpful_count
        if total_votes == 0:
            return 0
        return self.helpful_count / total_votes
    
    def save(self, *args, **kwargs):
        # Check if this is a verified purchase
        if self.order and self.order.status == 'completed':
            # Check if the order contains this artwork
            if self.order.items.filter(artwork=self.artwork).exists():
                self.is_verified_purchase = True
        
        super().save(*args, **kwargs)
        
        # Update artwork rating after saving review
        self.update_artwork_rating()
    
    def update_artwork_rating(self):
        """Update the artwork's average rating"""
        from django.db.models import Avg
        
        avg_rating = Review.objects.filter(
            artwork=self.artwork,
            is_approved=True
        ).aggregate(avg_rating=Avg('rating'))['avg_rating']
        
        if avg_rating:
            # Update artwork rating (you'd need to add this field to Artwork model)
            # self.artwork.average_rating = round(avg_rating, 2)
            # self.artwork.review_count = self.artwork.reviews.filter(is_approved=True).count()
            # self.artwork.save(update_fields=['average_rating', 'review_count'])
            pass


class ReviewHelpfulness(models.Model):
    """Track review helpfulness votes"""
    
    HELPFUL = 'helpful'
    NOT_HELPFUL = 'not_helpful'
    
    VOTE_CHOICES = [
        (HELPFUL, _('Helpful')),
        (NOT_HELPFUL, _('Not Helpful')),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpfulness_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_votes')
    vote = models.CharField(_('vote'), max_length=15, choices=VOTE_CHOICES)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        db_table = 'review_helpfulness'
        verbose_name = _('Review Helpfulness')
        verbose_name_plural = _('Review Helpfulness')
        unique_together = ['review', 'user']  # One vote per user per review
        indexes = [
            models.Index(fields=['review', 'vote']),
        ]
    
    def __str__(self):
        return f"{self.user.email} found review {self.review.id} {self.vote}"
    
    def save(self, *args, **kwargs):
        # Update review helpfulness counts
        old_vote = None
        if self.pk:
            old_vote = ReviewHelpfulness.objects.get(pk=self.pk).vote
        
        super().save(*args, **kwargs)
        
        # Update counts on the review
        if old_vote != self.vote:
            if old_vote == self.HELPFUL:
                self.review.helpful_count = max(0, self.review.helpful_count - 1)
            elif old_vote == self.NOT_HELPFUL:
                self.review.not_helpful_count = max(0, self.review.not_helpful_count - 1)
            
            if self.vote == self.HELPFUL:
                self.review.helpful_count += 1
            elif self.vote == self.NOT_HELPFUL:
                self.review.not_helpful_count += 1
            
            self.review.save(update_fields=['helpful_count', 'not_helpful_count'])


class ReviewResponse(models.Model):
    """Artist or admin response to reviews"""
    
    review = models.OneToOneField(Review, on_delete=models.CASCADE, related_name='response')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_responses')
    
    response_text = models.TextField(_('response text'))
    
    is_artist_response = models.BooleanField(_('is artist response'), default=False)
    is_admin_response = models.BooleanField(_('is admin response'), default=False)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'review_responses'
        verbose_name = _('Review Response')
        verbose_name_plural = _('Review Responses')
        ordering = ['-created_at']
    
    def __str__(self):
        response_type = "Artist" if self.is_artist_response else "Admin"
        return f"{response_type} response to review {self.review.id}"
    
    def save(self, *args, **kwargs):
        # Set response type based on user role
        if self.user.role == 'artist':
            self.is_artist_response = True
        elif self.user.role == 'admin':
            self.is_admin_response = True
        
        super().save(*args, **kwargs)


class ReviewReport(models.Model):
    """Report inappropriate reviews"""
    
    SPAM = 'spam'
    INAPPROPRIATE = 'inappropriate'
    FAKE = 'fake'
    OTHER = 'other'
    
    REASON_CHOICES = [
        (SPAM, _('Spam')),
        (INAPPROPRIATE, _('Inappropriate Content')),
        (FAKE, _('Fake Review')),
        (OTHER, _('Other')),
    ]
    
    PENDING = 'pending'
    REVIEWED = 'reviewed'
    RESOLVED = 'resolved'
    DISMISSED = 'dismissed'
    
    STATUS_CHOICES = [
        (PENDING, _('Pending')),
        (REVIEWED, _('Under Review')),
        (RESOLVED, _('Resolved')),
        (DISMISSED, _('Dismissed')),
    ]
    
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_reports')
    
    reason = models.CharField(_('reason'), max_length=15, choices=REASON_CHOICES)
    description = models.TextField(_('description'), blank=True)
    
    status = models.CharField(_('status'), max_length=15, choices=STATUS_CHOICES, default=PENDING)
    
    # Resolution
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_review_reports'
    )
    resolution_notes = models.TextField(_('resolution notes'), blank=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        db_table = 'review_reports'
        verbose_name = _('Review Report')
        verbose_name_plural = _('Review Reports')
        ordering = ['-created_at']
        unique_together = ['review', 'reported_by']  # One report per user per review
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['reason']),
        ]
    
    def __str__(self):
        return f"Report for review {self.review.id} - {self.get_reason_display()}"
