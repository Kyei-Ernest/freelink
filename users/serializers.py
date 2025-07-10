from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'phone', 'is_freelancer', 'is_client', 'language_preference',
                  'is_verified')


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password', 'is_freelancer', 'is_client')
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