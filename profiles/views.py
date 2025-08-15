from rest_framework import generics, permissions
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import (
    ProfileSerializer,
    ProfileUpdateSerializer,
    PublicProfileSerializer
)

User = get_user_model()


class MyProfileView(generics.RetrieveAPIView):
    """
    GET /profile/me/ → View your own profile
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class MyProfileUpdateView(generics.UpdateAPIView):
    """
    PATCH /profile/me/update/ → Update your own profile
    """
    serializer_class = ProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class PublicProfileView(generics.RetrieveAPIView):
    """
    GET /profile/<username>/ → View a public profile
    """
    serializer_class = PublicProfileSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'user__email'

    def get_queryset(self):
        return Profile.objects.select_related('user').all()
