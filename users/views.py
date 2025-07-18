from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from .models import User
from .serializers import (UserSerializer, RegisterSerializer,
                          LoginSerializer, ChangePasswordSerializer,
                          ResetPasswordSerializer, VerifyEmailSerializer)
from django.contrib.auth import update_session_auth_hash
import logging

from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

from wallet.models import Wallet
from notifications.models import Notification

# Set up logging
logger = logging.getLogger(__name__)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({"token": token.key, "user": user_data})


class LogoutView(APIView):
    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyPhoneView(APIView):
    def post(self, request):
        user = request.user
        user.is_verified = True
        user.save()
        return Response({"message": "Phone verified."})


class VerifyEmailView(APIView):
    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid user ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            """# Verify the user
            user.is_verified = True
            user.save()"""

            # Log the email verification
            logger.info(
                f"Email verified for user: {user.username} "
                f"(Phone: {user.phone}, Role: {'Freelancer' if user.is_freelancer else 'Client'})"
            )

            return Response(
                {
                    'message': f"Email verified successfully for {'freelancer' if user.is_freelancer else 'client'}"
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # Verify old password
            if not user.check_password(old_password):
                return Response(
                    {'old_password': 'Current password is incorrect'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password and save
            user.set_password(new_password)
            user.save()

            # Update session to prevent logout
            update_session_auth_hash(request, user)

            # Log the password change
            logger.info(
                f"Password changed for user: {user.username} (Phone: {user.phone}, Role: {'Freelancer' if user.is_freelancer else 'Client'})")

            return Response(
                {'message': f"Password changed successfully for {'freelancer' if user.is_freelancer else 'client'}"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated

class ResetPasswordView(APIView):
    permission_classes = [IsNotAuthenticated]  # Only allow unauthenticated users

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response(
                    {'error': 'Invalid user ID'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Set new password
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()

            # Log the password reset
            logger.info(
                f"Password reset for user: {user.username} "
                f"(Phone: {user.phone}, Role: {'Freelancer' if user.is_freelancer else 'Client'})"
            )

            return Response(
                {'message': f"Password reset successfully for {'freelancer' if user.is_freelancer else 'client'}"},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
