from django.contrib import admin
from .models import Review, ReviewHelpfulness, ReviewResponse, ReviewReport


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Review admin"""
    list_display = ('user', 'artwork', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'artwork__title')
    ordering = ('-created_at',)


@admin.register(ReviewHelpfulness)
class ReviewHelpfulnessAdmin(admin.ModelAdmin):
    """ReviewHelpfulness admin"""
    list_display = ('review', 'user', 'vote')
    list_filter = ('vote',)
    search_fields = ('review__user__email', 'user__email')
    ordering = ('-created_at',)


@admin.register(ReviewResponse)
class ReviewResponseAdmin(admin.ModelAdmin):
    """ReviewResponse admin"""
    list_display = ('review', 'user', 'created_at')
    search_fields = ('review__user__email', 'user__email')
    ordering = ('-created_at',)


@admin.register(ReviewReport)
class ReviewReportAdmin(admin.ModelAdmin):
    """ReviewReport admin"""
    list_display = ('review', 'reported_by', 'reason', 'status')
    list_filter = ('reason', 'status')
    search_fields = ('review__user__email', 'reported_by__email')
    ordering = ('-created_at',)
