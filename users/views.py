from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework.authtoken.models import Token
from .serializers import (UserSerializer, RegisterSerializer,
                          LoginSerializer, ChangePasswordSerializer,
                          ResetPasswordSerializer, VerifyEmailSerializer,
                          VerifyPhoneSerializer, PasswordResetRequestSerializer, EmptySerializer)
from django.contrib.auth import update_session_auth_hash
from django.core.cache import cache  # For storing verification codes temporarily
from rest_framework import throttling

from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
import logging

from wallet.models import Wallet
from notifications.models import Notification
from clients.models import ClientProfile
from freelancers.models import FreelancerProfile

from rest_framework import generics

logger = logging.getLogger(__name__)
User = get_user_model()


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
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        token, created = Token.objects.get_or_create(user=user)
        user_data = UserSerializer(user).data
        return Response({"token": token.key, "user": user_data})


class LogoutView(generics.GenericAPIView):
    serializer_class = EmptySerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    serializer_class = ChangePasswordSerializer
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
    serializer_class = ResetPasswordSerializer
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


class VerifyEmailView(APIView):
    permission_classes = [IsNotAuthenticated]
    throttle_classes = [throttling.AnonRateThrottle]

    def post(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uidb64']))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({'error': 'Invalid user ID'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()

            # Create profile if applicable
            if user.is_freelancer and not hasattr(user, 'freelancer_profile'):
                FreelancerProfile.objects.create(user=user)
            elif user.is_client and not hasattr(user, 'client_profile'):
                ClientProfile.objects.create(user=user)

            logger.info(
                f"Email verified for user: {user.username} "
                f"(Phone: {user.phone}, Role: {'Freelancer' if user.is_freelancer else 'Client'})"
            )
            return Response(
                {'message': f"Email verified successfully for {'freelancer' if user.is_freelancer else 'client'}"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyPhoneView(APIView):
    permission_classes = [IsNotAuthenticated]
    throttle_classes = [throttling.AnonRateThrottle]

    def post(self, request):
        serializer = VerifyPhoneSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = User.objects.get(phone=serializer.validated_data['phone'])
            except User.DoesNotExist:
                return Response({'error': 'No user found with this phone number'}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified = True
            user.save()

            # Create profile if applicable
            if user.is_freelancer and not hasattr(user, 'freelancer_profile'):
                FreelancerProfile.objects.create(user=user)
            elif user.is_client and not hasattr(user, 'client_profile'):
                ClientProfile.objects.create(user=user)

            cache.delete(f"phone_verification_{user.phone}")
            logger.info(
                f"Phone verified for user: {user.username} "
                f"(Phone: {user.phone}, Role: {'Freelancer' if user.is_freelancer else 'Client'})"
            )
            return Response(
                {'message': f"Phone verified successfully for {'freelancer' if user.is_freelancer else 'client'}"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(generics.CreateAPIView):
    permission_classes = [IsNotAuthenticated]
    throttle_classes = [throttling.AnonRateThrottle]
    serializer_class = PasswordResetRequestSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Always respond the same for security reasons
            return Response(
                {'message': 'If an account exists with this email, a reset link will be sent'},
                status=status.HTTP_200_OK
            )

        # Generate reset token
        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password/?uidb64={uidb64}&token={token}"

        # Send email
        send_mail(
            subject='Password Reset Request',
            message=f'Click the link to reset your password: {reset_url}',
            from_email='kookyei44@gmail.com',
            recipient_list=[user.email],
        )

        logger.info(f"Password reset link sent to {user.email} (Phone: {user.phone})")

        return Response(
            {'message': 'If an account exists with this email, a reset link will be sent'},
            status=status.HTTP_200_OK
        )


class SendVerificationEmailView(APIView):
    permission_classes = [IsNotAuthenticated]
    throttle_classes = [throttling.AnonRateThrottle]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email, is_verified=False)
        except User.DoesNotExist:
            return Response(
                {'message': 'If an unverified account exists, a verification link will be sent'},
                status=status.HTTP_200_OK
            )

        token = PasswordResetTokenGenerator().make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        verify_url = f"{request.scheme}://{request.get_host()}/verify-email/?uidb64={uidb64}&token={token}"

        send_mail(
            subject='Verify Your Email',
            message=f'Click the link to verify your email: {verify_url}',
            from_email='from@example.com',
            recipient_list=[user.email],
        )

        logger.info(f"Verification email sent to {user.email} (Phone: {user.phone})")
        return Response(
            {'message': 'If an unverified account exists, a verification link will be sent'},
            status=status.HTTP_200_OK
        )
