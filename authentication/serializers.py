from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from datetime import datetime
from .models import User, Address, AzamPayAuthToken


class UserRegistrationSerializer(serializers.ModelSerializer):
    """User registration serializer"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'phone', 'role', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    """User serializer"""
    
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'phone', 'role', 'locale', 'is_verified', 'avatar', 'date_of_birth',
            'date_joined', 'last_login'
        )
        read_only_fields = ('id', 'date_joined', 'last_login', 'is_verified')


class AddressSerializer(serializers.ModelSerializer):
    """Address serializer"""
    
    class Meta:
        model = Address
        fields = (
            'id', 'type', 'line1', 'line2', 'city', 'state', 'postal_code',
            'country', 'latitude', 'longitude', 'is_default', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        
        # If this is set as default, unset other defaults of the same type
        if validated_data.get('is_default', False):
            Address.objects.filter(
                user=validated_data['user'],
                type=validated_data['type']
            ).update(is_default=False)
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        # If this is set as default, unset other defaults of the same type
        if validated_data.get('is_default', False):
            Address.objects.filter(
                user=instance.user,
                type=instance.type
            ).exclude(id=instance.id).update(is_default=False)
        
        return super().update(instance, validated_data)


class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    
    email = serializers.EmailField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class PasswordChangeSerializer(serializers.Serializer):
    """Password change serializer"""
    
    old_password = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match")
        return attrs
    
    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect')
        return value
    
    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()


class AzamPayAuthSerializer(serializers.ModelSerializer):
    """Azam Pay authentication token serializer"""
    
    expires_in = serializers.CharField(write_only=True)
    
    class Meta:
        model = AzamPayAuthToken
        fields = ('access_token', 'refresh_token', 'token_type', 'expires_in')
    
    def create(self, validated_data):
        # Convert expire timestamp to datetime
        expire_timestamp = validated_data.pop('expires_in')
        
        if isinstance(expire_timestamp, str):
            # If it's a string timestamp, convert to datetime
            try:
                expire_datetime = datetime.fromtimestamp(int(expire_timestamp), tz=timezone.get_current_timezone())
            except (ValueError, TypeError):
                # If it's already a datetime string, parse it
                expire_datetime = datetime.fromisoformat(expire_timestamp.replace('Z', '+00:00'))
        else:
            expire_datetime = expire_timestamp
        
        validated_data['expires_in'] = expire_datetime
        
        # Delete old tokens to keep only the latest one
        AzamPayAuthToken.objects.all().delete()
        
        return super().create(validated_data)
        return user
