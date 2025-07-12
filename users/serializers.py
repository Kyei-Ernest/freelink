from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from wallet.models import Wallet
from notifications.models import Notification
from chat.models import Message

User = get_user_model()


# Wallet Serializer
class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']


# Notification Serializer
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']


# Message Preview Serializer
class MessagePreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'content', 'timestamp', 'is_read']


# User Serializer
class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)
    notifications = serializers.SerializerMethodField()
    unread_messages = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'is_freelancer',
            'is_client',
            'language_preference',
            'is_verified',
            'wallet',
            'notifications',
            'unread_messages',
        ]

    def get_notifications(self, obj):
        return Notification.objects.filter(user=obj, is_read=False).count()

    def get_unread_messages(self, obj):
        return Message.objects.filter(recipient=obj, is_read=False).count()


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'email', 'phone', 'password',
            'is_freelancer', 'is_client'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        is_freelancer = data.get('is_freelancer', False)
        is_client = data.get('is_client', False)

        if is_freelancer and is_client:
            raise serializers.ValidationError("A user cannot be both a freelancer and a client.")
        if not is_freelancer and not is_client:
            raise serializers.ValidationError("User must be either a freelancer or a client.")

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password'],
            is_freelancer=validated_data.get('is_freelancer', False),
            is_client=validated_data.get('is_client', False),
        )
        return user


# Login Serializer
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")
