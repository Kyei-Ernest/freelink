from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

User = get_user_model()

class ProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.ReadOnlyField(source='user.id')
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')
    full_name = serializers.ReadOnlyField(source='user.full_name')
    phone = serializers.ReadOnlyField(source='user.phone')
    language_preference = serializers.ReadOnlyField(source='user.language_preference')
    is_freelancer = serializers.ReadOnlyField(source='user.is_freelancer')
    is_client = serializers.ReadOnlyField(source='user.is_client')
    is_verified = serializers.ReadOnlyField(source='user.is_verified')
    is_phone_verified = serializers.ReadOnlyField(source='user.is_phone_verified')

    class Meta:
        model = Profile
        fields = [
            'user_id',
            'username',
            'email',
            'full_name',
            'phone',
            'language_preference',
            'is_freelancer',
            'is_client',
            'bio',
            'skills',
            'location',
            'website',
            'profile_picture',
            'is_verified',
            'is_phone_verified',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields


class ProfileUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.full_name', required=False)
    phone = serializers.CharField(source='user.phone', required=False)
    language_preference = serializers.CharField(source='user.language_preference', required=False)

    class Meta:
        model = Profile
        fields = [
            'full_name',
            'phone',
            'language_preference',
            'bio',
            'skills',
            'location',
            'website',
            'profile_picture'
        ]

    def update(self, instance, validated_data):
        # Handle user fields separately
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()

        # Update profile fields
        return super().update(instance, validated_data)


class PublicProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    full_name = serializers.ReadOnlyField(source='user.full_name')

    class Meta:
        model = Profile
        fields = [
            'username',
            'full_name',
            'bio',
            'skills',
            'location',
            'website',
            'profile_picture'
        ]
