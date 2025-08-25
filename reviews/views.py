from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from catalog.models import Artwork
from orders.models import Order
from .models import Review, ReviewHelpfulness, ReviewResponse, ReviewReport
from .forms import ReviewForm, ReviewResponseForm, ReviewReportForm
import json


class ReviewListView(ListView):
    """List all approved reviews"""
    model = Review
    template_name = 'reviews/review_list.html'
    context_object_name = 'reviews'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True).select_related(
            'user', 'artwork', 'order'
        ).prefetch_related('helpfulness_votes')
        
        # Filter by artwork if specified
        artwork_id = self.request.GET.get('artwork')
        if artwork_id:
            queryset = queryset.filter(artwork_id=artwork_id)
        
        # Filter by rating
        rating = self.request.GET.get('rating')
        if rating:
            queryset = queryset.filter(rating=rating)
        
        # Search in title and comment
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(comment__icontains=search)
            )
        
        # Sort by helpfulness, rating, or date
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by == 'helpfulness':
            queryset = queryset.annotate(
                helpfulness_score=Count('helpfulness_votes', filter=Q(helpfulness_votes__vote='helpful'))
            ).order_by('-helpfulness_score', '-created_at')
        elif sort_by == 'rating_high':
            queryset = queryset.order_by('-rating', '-created_at')
        elif sort_by == 'rating_low':
            queryset = queryset.order_by('rating', '-created_at')
        else:
            queryset = queryset.order_by('-created_at')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artwork'] = None
        
        artwork_id = self.request.GET.get('artwork')
        if artwork_id:
            context['artwork'] = get_object_or_404(Artwork, id=artwork_id)
            
        # Add rating statistics
        if context['artwork']:
            reviews_stats = Review.objects.filter(
                artwork_id=artwork_id,
                is_approved=True
            ).aggregate(
                avg_rating=Avg('rating'),
                total_reviews=Count('id'),
                five_star=Count('id', filter=Q(rating=5)),
                four_star=Count('id', filter=Q(rating=4)),
                three_star=Count('id', filter=Q(rating=3)),
                two_star=Count('id', filter=Q(rating=2)),
                one_star=Count('id', filter=Q(rating=1)),
            )
            context['reviews_stats'] = reviews_stats
        
        return context


class ReviewDetailView(DetailView):
    """View a single review with responses"""
    model = Review
    template_name = 'reviews/review_detail.html'
    context_object_name = 'review'
    
    def get_queryset(self):
        return Review.objects.filter(is_approved=True).select_related(
            'user', 'artwork', 'order'
        ).prefetch_related('helpfulness_votes', 'response')


@method_decorator(login_required, name='dispatch')
class ReviewCreateView(CreateView):
    """Create a new review"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'
    
    def dispatch(self, request, *args, **kwargs):
        self.artwork = get_object_or_404(Artwork, id=kwargs['artwork_id'])
        
        # Check if user already reviewed this artwork
        if Review.objects.filter(user=request.user, artwork=self.artwork).exists():
            messages.error(request, 'You have already reviewed this artwork.')
            return redirect('catalog:artwork_detail', pk=self.artwork.id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['artwork'] = self.artwork
        return kwargs
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.artwork = self.artwork
        
        # Check if this is a verified purchase
        order_id = self.request.POST.get('order')
        if order_id:
            try:
                order = Order.objects.get(
                    id=order_id,
                    user=self.request.user,
                    status='completed'
                )
                # Verify the order contains this artwork
                if order.items.filter(artwork=self.artwork).exists():
                    form.instance.order = order
            except Order.DoesNotExist:
                pass
        
        messages.success(self.request, 'Your review has been submitted successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalog:artwork_detail', kwargs={'pk': self.artwork.id})
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['artwork'] = self.artwork
        
        # Get user's completed orders that contain this artwork
        context['eligible_orders'] = Order.objects.filter(
            user=self.request.user,
            status='completed',
            items__artwork=self.artwork
        ).distinct()
        
        return context


@method_decorator(login_required, name='dispatch')
class ReviewUpdateView(UpdateView):
    """Update an existing review"""
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'
    
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['artwork'] = self.object.artwork
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Your review has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('catalog:artwork_detail', kwargs={'pk': self.object.artwork.id})


@login_required
@require_POST
def review_helpfulness_vote(request, review_id):
    """Vote on review helpfulness"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    vote_type = request.POST.get('vote')
    
    if vote_type not in ['helpful', 'not_helpful']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    # Check if user is trying to vote on their own review
    if review.user == request.user:
        return JsonResponse({'error': 'You cannot vote on your own review'}, status=400)
    
    # Get or create vote
    vote, created = ReviewHelpfulness.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'vote': vote_type}
    )
    
    if not created:
        # Update existing vote
        vote.vote = vote_type
        vote.save()
    
    # Return updated counts
    return JsonResponse({
        'helpful_count': review.helpful_count,
        'not_helpful_count': review.not_helpful_count,
        'user_vote': vote_type
    })


@login_required
def review_response_create(request, review_id):
    """Create a response to a review"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    
    # Check if user can respond (artist of the artwork or admin)
    can_respond = (
        request.user.is_staff or 
        (hasattr(request.user, 'artist_profile') and 
         request.user.artist_profile == review.artwork.artist)
    )
    
    if not can_respond:
        messages.error(request, 'You do not have permission to respond to this review.')
        return redirect('reviews:review_detail', pk=review_id)
    
    # Check if response already exists
    if hasattr(review, 'response'):
        messages.error(request, 'A response already exists for this review.')
        return redirect('reviews:review_detail', pk=review_id)
    
    if request.method == 'POST':
        form = ReviewResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.review = review
            response.user = request.user
            response.save()
            
            messages.success(request, 'Your response has been posted successfully!')
            return redirect('reviews:review_detail', pk=review_id)
    else:
        form = ReviewResponseForm()
    
    return render(request, 'reviews/review_response_form.html', {
        'form': form,
        'review': review
    })


@login_required
def review_report_create(request, review_id):
    """Report a review"""
    review = get_object_or_404(Review, id=review_id, is_approved=True)
    
    # Check if user already reported this review
    if ReviewReport.objects.filter(review=review, reported_by=request.user).exists():
        messages.error(request, 'You have already reported this review.')
        return redirect('reviews:review_detail', pk=review_id)
    
    # User cannot report their own review
    if review.user == request.user:
        messages.error(request, 'You cannot report your own review.')
        return redirect('reviews:review_detail', pk=review_id)
    
    if request.method == 'POST':
        form = ReviewReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.review = review
            report.reported_by = request.user
            report.save()
            
            messages.success(request, 'Thank you for reporting this review. We will investigate it.')
            return redirect('reviews:review_detail', pk=review_id)
    else:
        form = ReviewReportForm()
    
    return render(request, 'reviews/review_report_form.html', {
        'form': form,
        'review': review
    })


@login_required
def user_reviews(request):
    """List user's own reviews"""
    reviews = Review.objects.filter(user=request.user).select_related(
        'artwork', 'order'
    ).order_by('-created_at')
    
    paginator = Paginator(reviews, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reviews/user_reviews.html', {
        'page_obj': page_obj,
        'reviews': page_obj
    })


@login_required
@require_POST
def review_delete(request, review_id):
    """Delete a review (only by the review author)"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    artwork_id = review.artwork.id
    review.delete()
    
    messages.success(request, 'Your review has been deleted.')
    return redirect('catalog:artwork_detail', pk=artwork_id)


def artwork_reviews_api(request, artwork_id):
    """API endpoint for artwork reviews (for AJAX loading)"""
    artwork = get_object_or_404(Artwork, id=artwork_id)
    
    # Pagination
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    
    # Filters
    rating_filter = request.GET.get('rating')
    sort_by = request.GET.get('sort', '-created_at')
    
    queryset = Review.objects.filter(
        artwork=artwork,
        is_approved=True
    ).select_related('user')
    
    if rating_filter:
        queryset = queryset.filter(rating=rating_filter)
    
    # Sorting
    if sort_by == 'helpfulness':
        queryset = queryset.annotate(
            helpfulness_score=Count('helpfulness_votes', filter=Q(helpfulness_votes__vote='helpful'))
        ).order_by('-helpfulness_score', '-created_at')
    elif sort_by == 'rating_high':
        queryset = queryset.order_by('-rating', '-created_at')
    elif sort_by == 'rating_low':
        queryset = queryset.order_by('rating', '-created_at')
    else:
        queryset = queryset.order_by('-created_at')
    
    paginator = Paginator(queryset, page_size)
    page_obj = paginator.get_page(page)
    
    # Serialize reviews
    reviews_data = []
    for review in page_obj:
        user_vote = None
        if request.user.is_authenticated:
            vote_obj = review.helpfulness_votes.filter(user=request.user).first()
            if vote_obj:
                user_vote = vote_obj.vote
        
        reviews_data.append({
            'id': review.id,
            'user': {
                'name': review.user.get_full_name() or review.user.email,
                'avatar': getattr(review.user, 'avatar', {}).get('url', '') if hasattr(review.user, 'avatar') else ''
            },
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'is_verified_purchase': review.is_verified_purchase,
            'helpful_count': review.helpful_count,
            'not_helpful_count': review.not_helpful_count,
            'user_vote': user_vote,
            'created_at': review.created_at.isoformat(),
            'response': {
                'text': review.response.response_text,
                'user': review.response.user.get_full_name() or review.response.user.email,
                'is_artist': review.response.is_artist_response,
                'created_at': review.response.created_at.isoformat()
            } if hasattr(review, 'response') else None
        })
    
    return JsonResponse({
        'reviews': reviews_data,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page': page,
        'total_pages': paginator.num_pages,
        'total_count': paginator.count
    })


# Helper function to check if user can review artwork
def can_user_review_artwork(user, artwork):
    """Check if a user can review an artwork"""
    if not user.is_authenticated:
        return False, "You must be logged in to review"
    
    # Check if user already reviewed
    if Review.objects.filter(user=user, artwork=artwork).exists():
        return False, "You have already reviewed this artwork"
    
    # Check if user purchased the artwork
    has_purchased = Order.objects.filter(
        user=user,
        status='completed',
        items__artwork=artwork
    ).exists()
    
    if not has_purchased:
        return False, "You can only review artworks you have purchased"
    
    return True, "Can review"
