from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    # API Endpoints (Primary - DRF)
    # Public review endpoints
    path('', views.ReviewListView.as_view(), name='api-review-list'),
    path('<int:pk>/', views.ReviewDetailView.as_view(), name='api-review-detail'),
    
    # Review CRUD (authenticated users)
    path('artwork/<int:artwork_id>/create/', views.ReviewCreateView.as_view(), name='api-review-create'),
    path('<int:pk>/update/', views.ReviewUpdateView.as_view(), name='api-review-update'),
    path('<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='api-review-delete'),
    
    # Review interactions
    path('<int:review_id>/helpfulness/', views.ReviewHelpfulnessView.as_view(), name='api-review-helpfulness'),
    path('<int:review_id>/respond/', views.ReviewResponseCreateView.as_view(), name='api-review-respond'),
    path('<int:review_id>/report/', views.ReviewReportCreateView.as_view(), name='api-review-report'),
    
    # Statistics and user reviews
    path('artwork/<int:artwork_id>/stats/', views.ArtworkReviewStatsView.as_view(), name='api-artwork-review-stats'),
    path('user/', views.UserReviewsView.as_view(), name='api-my-reviews'),
    path('user/<int:user_id>/', views.UserReviewsView.as_view(), name='api-user-reviews'),
    
    # Admin/Moderation endpoints
    path('<int:pk>/moderate/', views.ReviewModerationView.as_view(), name='api-review-moderate'),
    path('admin/pending/', views.PendingReviewsView.as_view(), name='api-pending-reviews'),
    path('admin/reported/', views.ReportedReviewsView.as_view(), name='api-reported-reviews'),
]
