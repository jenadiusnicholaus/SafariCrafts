"""
Reviews Views - API-First Architecture
======================================

This module contains all review-related views using Django REST Framework.
All endpoints are JSON API based for consistency with SafariCrafts architecture.

API Documentation: /api/docs/
Base URL: /api/v1/reviews/
"""

from rest_framework import generics, permissions, status, filters, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg, Count, Prefetch
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from catalog.models import Artwork
from orders.models import Order
from .models import Review, ReviewHelpfulness, ReviewResponse, ReviewReport
from .serializers import (
    ReviewListSerializer, ReviewDetailSerializer, ReviewCreateSerializer, 
    ReviewUpdateSerializer, ReviewHelpfulnessSerializer, ReviewResponseSerializer,
    ReviewReportSerializer, ReviewStatsSerializer, ReviewModerationSerializer
)


class ReviewListView(generics.ListAPIView):
    """List all approved reviews with filtering and pagination"""
    
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'is_verified_purchase']
    search_fields = ['title', 'comment', 'user__first_name', 'user__last_name']
    ordering_fields = ['created_at', 'rating', 'helpful_count']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True).select_related(
            'user', 'artwork'
        ).prefetch_related('helpfulness_votes')
        
        # Filter by artwork if specified
        artwork_id = self.request.query_params.get('artwork')
        if artwork_id:
            queryset = queryset.filter(artwork_id=artwork_id)
        
        # Add response count annotation
        queryset = queryset.annotate(
            response_count=Count('response')
        )
        
        # Custom ordering by helpfulness
        ordering = self.request.query_params.get('ordering')
        if ordering == 'helpfulness':
            queryset = queryset.annotate(
                helpfulness_score=Count('helpfulness_votes', filter=Q(helpfulness_votes__vote='helpful'))
            ).order_by('-helpfulness_score', '-created_at')
        
        return queryset
    
    @extend_schema(
        summary="List reviews",
        description="Get a paginated list of approved reviews with optional filtering",
        parameters=[
            OpenApiParameter(name='artwork', description='Filter by artwork ID', type=int),
            OpenApiParameter(name='rating', description='Filter by rating (1-5)', type=int),
            OpenApiParameter(name='is_verified_purchase', description='Filter by verified purchases', type=bool),
            OpenApiParameter(name='search', description='Search in title and comment', type=str),
            OpenApiParameter(name='ordering', description='Order by: created_at, -created_at, rating, -rating, helpful_count, -helpful_count, helpfulness', type=str),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ReviewDetailView(generics.RetrieveAPIView):
    """View a single review with responses"""
    
    queryset = Review.objects.filter(is_approved=True).select_related(
        'user', 'artwork'
    ).prefetch_related(
        'response',
        'helpfulness_votes'
    )
    serializer_class = ReviewDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get review details",
        description="Get detailed information about a specific review including responses"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ReviewCreateView(generics.CreateAPIView):
    """Create a new review for an artwork"""
    
    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        artwork_id = self.kwargs.get('artwork_id')
        context['artwork'] = get_object_or_404(Artwork, id=artwork_id)
        return context
    
    @extend_schema(
        summary="Create a review",
        description="Create a new review for an artwork. User must be authenticated and cannot review the same artwork twice."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ReviewUpdateView(generics.RetrieveUpdateAPIView):
    """Update a user's own review"""
    
    serializer_class = ReviewUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only update their own reviews
        return Review.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Update a review",
        description="Update your own review. You can only edit reviews you created."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get review for editing",
        description="Get your own review details for editing"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ReviewDeleteView(generics.DestroyAPIView):
    """Delete a user's own review"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only delete their own reviews
        return Review.objects.filter(user=self.request.user)
    
    @extend_schema(
        summary="Delete a review",
        description="Delete your own review. This action cannot be undone."
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)


class ReviewHelpfulnessView(APIView):
    """Vote on review helpfulness"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Vote on review helpfulness",
        description="Vote whether a review was helpful or not. You can change your vote or remove it.",
        request=ReviewHelpfulnessSerializer,
        responses={
            200: OpenApiResponse(description="Vote updated successfully"),
            201: OpenApiResponse(description="Vote created successfully"),
            204: OpenApiResponse(description="Vote removed successfully"),
        }
    )
    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id, is_approved=True)
        
        # Users cannot vote on their own reviews
        if review.user == request.user:
            return Response(
                {'error': 'You cannot vote on your own review'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = ReviewHelpfulnessSerializer(
            data=request.data,
            context={'request': request, 'review': review}
        )
        
        if serializer.is_valid():
            # Check if user already has a vote
            existing_vote = ReviewHelpfulness.objects.filter(
                review=review, 
                user=request.user
            ).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.vote = serializer.validated_data['vote']
                existing_vote.save()
                
                # Update review helpfulness counts
                self._update_helpfulness_counts(review)
                
                return Response(
                    ReviewHelpfulnessSerializer(existing_vote).data,
                    status=status.HTTP_200_OK
                )
            else:
                # Create new vote
                helpfulness = serializer.save()
                
                # Update review helpfulness counts
                self._update_helpfulness_counts(review)
                
                return Response(
                    ReviewHelpfulnessSerializer(helpfulness).data,
                    status=status.HTTP_201_CREATED
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @extend_schema(
        summary="Remove helpfulness vote",
        description="Remove your vote on review helpfulness"
    )
    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)
        
        vote = ReviewHelpfulness.objects.filter(
            review=review, 
            user=request.user
        ).first()
        
        if vote:
            vote.delete()
            # Update review helpfulness counts
            self._update_helpfulness_counts(review)
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {'error': 'Vote not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    def _update_helpfulness_counts(self, review):
        """Update helpfulness counts on the review"""
        helpful_count = ReviewHelpfulness.objects.filter(
            review=review, 
            vote='helpful'
        ).count()
        
        not_helpful_count = ReviewHelpfulness.objects.filter(
            review=review, 
            vote='not_helpful'
        ).count()
        
        review.helpful_count = helpful_count
        review.not_helpful_count = not_helpful_count
        review.save(update_fields=['helpful_count', 'not_helpful_count'])


class ReviewResponseCreateView(generics.CreateAPIView):
    """Create a response to a review"""
    
    serializer_class = ReviewResponseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        review_id = self.kwargs.get('review_id')
        context['review'] = get_object_or_404(Review, id=review_id)
        return context
    
    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        
        # Check if user already responded to this review
        if ReviewResponse.objects.filter(review=review, user=self.request.user).exists():
            raise serializers.ValidationError("You have already responded to this review.")
        
        serializer.save(user=self.request.user, review=review)
    
    @extend_schema(
        summary="Respond to a review",
        description="Create a response to a review. You can only respond once per review."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ReviewReportCreateView(generics.CreateAPIView):
    """Report an inappropriate review"""
    
    serializer_class = ReviewReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        review_id = self.kwargs.get('review_id')
        context['review'] = get_object_or_404(Review, id=review_id)
        return context
    
    @extend_schema(
        summary="Report a review",
        description="Report a review for inappropriate content. You can only report each review once."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ArtworkReviewStatsView(APIView):
    """Get review statistics for an artwork"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        summary="Get artwork review statistics",
        description="Get comprehensive review statistics for a specific artwork",
        responses={200: ReviewStatsSerializer}
    )
    def get(self, request, artwork_id):
        artwork = get_object_or_404(Artwork, id=artwork_id)
        
        stats_data = {'artwork_id': artwork_id}
        serializer = ReviewStatsSerializer(stats_data)
        
        return Response(serializer.data)


class UserReviewsView(generics.ListAPIView):
    """Get reviews by a specific user"""
    
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        if user_id:
            # Public view of user's reviews (only approved ones)
            return Review.objects.filter(
                user_id=user_id, 
                is_approved=True
            ).select_related('user', 'artwork')
        else:
            # Current user's own reviews (including pending ones)
            return Review.objects.filter(
                user=self.request.user
            ).select_related('user', 'artwork')
    
    @extend_schema(
        summary="Get user reviews",
        description="Get reviews by a specific user or your own reviews if no user_id provided"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Admin/Moderation Views
class ReviewModerationView(generics.UpdateAPIView):
    """Moderate reviews (admin only)"""
    
    queryset = Review.objects.all()
    serializer_class = ReviewModerationSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        summary="Moderate a review",
        description="Approve, reject, or feature a review. Admin only."
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PendingReviewsView(generics.ListAPIView):
    """List pending reviews for moderation"""
    
    queryset = Review.objects.filter(is_approved=False).select_related('user', 'artwork')
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    @extend_schema(
        summary="List pending reviews",
        description="Get all reviews pending moderation. Admin only."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ReportedReviewsView(generics.ListAPIView):
    """List reported reviews for moderation"""
    
    serializer_class = ReviewListSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        # Get reviews that have been reported
        reported_review_ids = ReviewReport.objects.filter(
            status='pending'
        ).values_list('review_id', flat=True)
        
        return Review.objects.filter(
            id__in=reported_review_ids
        ).select_related('user', 'artwork').prefetch_related('reports')
    
    @extend_schema(
        summary="List reported reviews",
        description="Get all reviews that have been reported and need moderation. Admin only."
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
