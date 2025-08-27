from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg
from django.db import models
from catalog.models import Artwork
from orders.models import Order
from .models import Review, ReviewHelpfulness, ReviewResponse, ReviewReport

User = get_user_model()


class ReviewerSerializer(serializers.ModelSerializer):
    """Serializer for review author information"""
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'avatar']
        read_only_fields = ['id', 'first_name', 'last_name', 'avatar']
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Provide display name
        data['display_name'] = f"{instance.first_name} {instance.last_name}".strip() or "Anonymous"
        return data


class ReviewHelpfulnessSerializer(serializers.ModelSerializer):
    """Serializer for review helpfulness votes"""
    
    class Meta:
        model = ReviewHelpfulness
        fields = ['id', 'vote', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def create(self, validated_data):
        # Set the user from the request context
        user = self.context['request'].user
        review = self.context['review']
        
        # Check if user already voted on this review
        helpfulness, created = ReviewHelpfulness.objects.update_or_create(
            review=review,
            user=user,
            defaults={'vote': validated_data['vote']}
        )
        return helpfulness


class ReviewResponseSerializer(serializers.ModelSerializer):
    """Serializer for review responses"""
    
    user = ReviewerSerializer(read_only=True)
    
    class Meta:
        model = ReviewResponse
        fields = ['id', 'user', 'response_text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_response_text(self):
        response_text = self.validated_data.get('response_text', '').strip()
        
        if not response_text:
            raise serializers.ValidationError("Response text is required.")
        
        if len(response_text) < 10:
            raise serializers.ValidationError("Response must be at least 10 characters long.")
        
        return response_text


class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for reporting reviews"""
    
    class Meta:
        model = ReviewReport
        fields = ['id', 'reason', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def validate(self, data):
        # If "other" reason is selected, description should be provided
        if data.get('reason') == 'other' and not data.get('description', '').strip():
            raise serializers.ValidationError({
                'description': "Please provide a description when selecting 'Other' as the reason."
            })
        return data
    
    def create(self, validated_data):
        # Set the user and review from context
        user = self.context['request'].user
        review = self.context['review']
        
        # Check if user already reported this review
        if ReviewReport.objects.filter(review=review, reported_by=user).exists():
            raise serializers.ValidationError("You have already reported this review.")
        
        return ReviewReport.objects.create(
            review=review,
            reported_by=user,
            **validated_data
        )


class ReviewListSerializer(serializers.ModelSerializer):
    """Serializer for listing reviews (minimal data)"""
    
    user = ReviewerSerializer(read_only=True)
    helpfulness_score = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    response_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'user', 'rating', 'title', 'comment', 'is_verified_purchase',
            'helpful_count', 'not_helpful_count', 'helpfulness_score',
            'user_vote', 'response_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'is_verified_purchase', 'helpful_count', 
            'not_helpful_count', 'created_at', 'updated_at'
        ]
    
    def get_helpfulness_score(self, obj):
        """Calculate helpfulness score (helpful votes - not helpful votes)"""
        return obj.helpful_count - obj.not_helpful_count
    
    def get_user_vote(self, obj):
        """Get current user's vote on this review"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = ReviewHelpfulness.objects.filter(
                review=obj, 
                user=request.user
            ).first()
            return vote.vote if vote else None
        return None
    
    def get_response_count(self, obj):
        """Get count of responses to this review"""
        return getattr(obj, 'response_count', 0)


class ReviewDetailSerializer(ReviewListSerializer):
    """Serializer for detailed review view"""
    
    responses = ReviewResponseSerializer(many=True, read_only=True, source='response')
    artwork_title = serializers.CharField(source='artwork.title', read_only=True)
    
    class Meta(ReviewListSerializer.Meta):
        fields = ReviewListSerializer.Meta.fields + [
            'responses', 'artwork_title', 'images'
        ]


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'images']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add helpful field descriptions
        self.fields['rating'].help_text = 'Rate this artwork from 1 to 5 stars'
        self.fields['title'].help_text = 'Optional: A brief summary of your review'
        self.fields['comment'].help_text = 'Share your experience with this artwork'
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value is None or value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
    
    def validate(self, data):
        """Ensure at least title or comment is provided"""
        title = data.get('title', '').strip()
        comment = data.get('comment', '').strip()
        
        if not title and not comment:
            raise serializers.ValidationError(
                "Please provide either a review title or comment."
            )
        
        return data
    
    def create(self, validated_data):
        # Set user and artwork from context
        user = self.context['request'].user
        artwork = self.context['artwork']
        
        # Check if user already reviewed this artwork
        if Review.objects.filter(user=user, artwork=artwork).exists():
            raise serializers.ValidationError(
                "You have already reviewed this artwork."
            )
        
        # Check if user purchased this artwork (for verified purchase flag)
        has_purchased = Order.objects.filter(
            user=user,
            items__artwork=artwork,
            status__in=['completed', 'delivered']
        ).exists()
        
        return Review.objects.create(
            user=user,
            artwork=artwork,
            is_verified_purchase=has_purchased,
            **validated_data
        )


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'title', 'comment', 'images']
    
    def validate_rating(self, value):
        """Validate rating is between 1 and 5"""
        if value is None or value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5 stars.")
        return value
    
    def validate(self, data):
        """Ensure at least title or comment is provided"""
        title = data.get('title', '').strip()
        comment = data.get('comment', '').strip()
        
        # Get current values if not in update data
        if not title and 'title' not in data:
            title = self.instance.title
        if not comment and 'comment' not in data:
            comment = self.instance.comment
        
        if not title and not comment:
            raise serializers.ValidationError(
                "Please provide either a review title or comment."
            )
        
        return data


class ReviewStatsSerializer(serializers.Serializer):
    """Serializer for review statistics"""
    
    total_reviews = serializers.IntegerField()
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    rating_distribution = serializers.DictField()
    verified_purchase_count = serializers.IntegerField()
    
    def to_representation(self, instance):
        """Calculate review statistics for an artwork"""
        artwork_id = instance.get('artwork_id')
        
        if not artwork_id:
            return super().to_representation(instance)
        
        reviews = Review.objects.filter(
            artwork_id=artwork_id,
            is_approved=True
        )
        
        # Calculate statistics
        total_reviews = reviews.count()
        
        if total_reviews == 0:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'rating_distribution': {str(i): 0 for i in range(1, 6)},
                'verified_purchase_count': 0
            }
        
        # Rating statistics
        rating_stats = reviews.aggregate(
            avg_rating=models.Avg('rating'),
            verified_count=Count('id', filter=Q(is_verified_purchase=True))
        )
        
        # Rating distribution
        rating_distribution = {}
        for i in range(1, 6):
            count = reviews.filter(rating=i).count()
            rating_distribution[str(i)] = count
        
        return {
            'total_reviews': total_reviews,
            'average_rating': round(rating_stats['avg_rating'] or 0, 2),
            'rating_distribution': rating_distribution,
            'verified_purchase_count': rating_stats['verified_count']
        }


class ReviewModerationSerializer(serializers.ModelSerializer):
    """Serializer for moderating reviews (admin only)"""
    
    moderation_notes = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Internal notes about this moderation action'
    )
    
    class Meta:
        model = Review
        fields = ['is_approved', 'is_featured', 'moderation_notes']
    
    def update(self, instance, validated_data):
        # Remove moderation_notes from validated_data as it's not a model field
        moderation_notes = validated_data.pop('moderation_notes', '')
        
        # Update the review
        review = super().update(instance, validated_data)
        
        # Log moderation action if notes provided
        if moderation_notes:
            # You could log this to a moderation log model if needed
            pass
        
        return review
