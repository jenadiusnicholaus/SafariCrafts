from rest_framework import serializers
from .models import Artist, Payout


class ArtistPublicSerializer(serializers.ModelSerializer):
    """Public artist information serializer"""
    
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = Artist
        fields = (
            'id', 'display_name', 'full_name', 'bio', 'tribe', 'region',
            'website', 'instagram', 'facebook', 'twitter',
            'total_sales', 'total_artworks', 'average_rating', 'is_verified'
        )
        read_only_fields = fields


class ArtistSerializer(serializers.ModelSerializer):
    """Artist profile serializer for authenticated users"""
    
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Artist
        fields = (
            'id', 'user', 'display_name', 'bio', 'tribe', 'region',
            'kyc_status', 'website', 'instagram', 'facebook', 'twitter',
            'id_number', 'bank_name', 'bank_account_number', 'mobile_wallet_number',
            'total_sales', 'total_artworks', 'average_rating', 'is_active',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'user', 'kyc_status', 'total_sales', 'total_artworks',
            'average_rating', 'created_at', 'updated_at'
        )
    
    def get_user(self, obj):
        from authentication.serializers import UserSerializer
        return UserSerializer(obj.user).data


class PayoutSerializer(serializers.ModelSerializer):
    """Payout serializer"""
    
    artist_name = serializers.CharField(source='artist.display_name', read_only=True)
    
    class Meta:
        model = Payout
        fields = (
            'id', 'artist_name', 'amount', 'currency', 'status', 'provider',
            'provider_ref', 'notes', 'processed_by', 'processed_at',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'artist_name', 'provider_ref', 'processed_by',
            'processed_at', 'created_at', 'updated_at'
        )
