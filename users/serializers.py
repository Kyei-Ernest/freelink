from django.contrib.auth import authenticate, get_user_model
from rest_framework import serializers

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from django.core.cache import cache  # For storing verification codes temporarily

from wallet.models import Wallet
from notifications.models import Notification


User = get_user_model()

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'is_read', 'created_at']

class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, write_only=True)
    uidb64 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uidb64': 'Invalid user ID'})
        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({'token': 'Invalid or expired token'})
        if user.is_verified:
            raise serializers.ValidationError({'error': 'Email is already verified'})
        return data

class UserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)
    notifications = serializers.SerializerMethodField()
    #unread_messages = serializers.SerializerMethodField()

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
            #'unread_messages',
        ]

    def get_notifications(self, obj):
        return Notification.objects.filter(user=obj, is_read=False).count()

    """def get_unread_messages(self, obj):
        return Message.objects.filter(recipient=obj, is_read=False).count()"""

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

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid credentials")

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Check if new password matches old password
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({'new_password': 'New password must be different from the old password'})

        # Check if new password matches confirmation
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'New passwords do not match'})

        # Check minimum password length
        if len(data['new_password']) < 8:
            raise serializers.ValidationError({'new_password': 'New password must be at least 8 characters long'})

        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True, write_only=True)
    uidb64 = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        # Check if new passwords match
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({'confirm_new_password': 'New passwords do not match'})

        # Check minimum password length
        if len(data['new_password']) < 8:
            raise serializers.ValidationError({'new_password': 'New password must be at least 8 characters long'})

        # Validate token and user
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'uidb64': 'Invalid user ID'})

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({'token': 'Invalid or expired token'})

        return data

class VerifyPhoneSerializer(serializers.Serializer):
    phone = serializers.CharField(required=True, write_only=True)
    code = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(phone=data['phone'])
        except User.DoesNotExist:
            raise serializers.ValidationError({'phone': 'No user found with this phone number'})
        if user.is_verified:
            raise serializers.ValidationError({'phone': 'Phone number is already verified'})
        cached_code = cache.get(f"phone_verification_{user.phone}")
        if not cached_code or cached_code != data['code']:
            raise serializers.ValidationError({'code': 'Invalid or expired verification code'})
        return data

class SendVerificationEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class EmptySerializer(serializers.Serializer):
    """Serializer for endpoints that don't require input."""
    pass

