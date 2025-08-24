from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import login
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import User, Address
from .serializers import (
    UserRegistrationSerializer, UserSerializer, AddressSerializer,
    LoginSerializer, PasswordChangeSerializer
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        operation_id='register_user',
        summary='Register a new user',
        description='Create a new user account',
        responses={
            201: OpenApiResponse(description='User created successfully'),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """User login endpoint"""
    
    permission_classes = [permissions.AllowAny]
    
    @extend_schema(
        operation_id='login_user',
        summary='User login',
        description='Authenticate user and return tokens',
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description='Login successful'),
            400: OpenApiResponse(description='Invalid credentials'),
        }
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserSerializer(user).data,
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """User logout endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        operation_id='logout_user',
        summary='User logout',
        description='Blacklist refresh token',
        responses={
            200: OpenApiResponse(description='Logout successful'),
        }
    )
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Logout successful'})
        except Exception:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    @extend_schema(
        operation_id='get_user_profile',
        summary='Get user profile',
        description='Retrieve current user profile',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='update_user_profile',
        summary='Update user profile',
        description='Update current user profile',
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class PasswordChangeView(APIView):
    """Password change endpoint"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        operation_id='change_password',
        summary='Change password',
        description='Change user password',
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description='Password changed successfully'),
            400: OpenApiResponse(description='Validation error'),
        }
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Password changed successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    """Address list and create endpoint"""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    @extend_schema(
        operation_id='list_addresses',
        summary='List user addresses',
        description='Retrieve all addresses for the current user',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='create_address',
        summary='Create address',
        description='Create a new address for the current user',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Address detail endpoint"""
    
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
    
    @extend_schema(
        operation_id='get_address',
        summary='Get address',
        description='Retrieve a specific address',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='update_address',
        summary='Update address',
        description='Update a specific address',
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
    
    @extend_schema(
        operation_id='delete_address',
        summary='Delete address',
        description='Delete a specific address',
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
