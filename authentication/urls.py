from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, LoginView, LogoutView, UserProfileView,
    PasswordChangeView, AddressListCreateView, AddressDetailView
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Profile
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),
    
    # Addresses
    path('addresses/', AddressListCreateView.as_view(), name='address_list'),
    path('addresses/<int:pk>/', AddressDetailView.as_view(), name='address_detail'),
]
