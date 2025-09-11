from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .models import Wallet, Currency
from .serializers import CurrencySerializer,WalletSerializer

import logging


logger = logging.getLogger(__name__)



class WalletView(APIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        if not (request.user.is_client or request.user.is_freelancer):
            return Response(
                {'error': 'Only profiles or freelancers can access their wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to access wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            wallet = request.user.wallet
            serializer = WalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )





class IsAdminUser(permissions.BasePermission):
    """Custom permission: allow only admins."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAdminUser]
