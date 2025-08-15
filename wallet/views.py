from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .models import Wallet
import logging

from .serializers import WalletSerializer

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

    def post(self, request):
        if not (request.user.is_client or request.user.is_freelancer):
            return Response(
                {'error': 'Only profiles or freelancers can create a wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to create a wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        if hasattr(request.user, 'wallet'):
            return Response(
                {'error': 'Wallet already exists'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = WalletSerializer(data={'balance': 0.00})
        if serializer.is_valid():
            serializer.save(user=request.user)
            logger.info(
                f"Wallet created for user: {request.user.username} "
                f"(Phone: {request.user.phone}, Role: {'Freelancer' if request.user.is_freelancer else 'Client'})"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        if not (request.user.is_client or request.user.is_freelancer):
            return Response(
                {'error': 'Only profiles or freelancers can manage their wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to manage wallet'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            wallet = request.user.wallet
        except Wallet.DoesNotExist:
            return Response(
                {'error': 'Wallet not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        action = request.data.get('action')  # 'deposit' or 'withdraw'
        amount = request.data.get('amount', 0)
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return Response(
                {'error': 'Amount must be a valid number'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if action == 'deposit':
            try:
                wallet.deposit(amount)
                logger.info(
                    f"Deposit of {amount} to wallet of {request.user.username} "
                    f"(Phone: {request.user.phone}, New Balance: {wallet.balance})"
                )
                return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        elif action == 'withdraw':
            try:
                wallet.withdraw(amount)
                logger.info(
                    f"Withdrawal of {amount} from wallet of {request.user.username} "
                    f"(Phone: {request.user.phone}, New Balance: {wallet.balance})"
                )
                return Response(WalletSerializer(wallet).data, status=status.HTTP_200_OK)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                {'error': 'Invalid action. Must be "deposit" or "withdraw"'},
                status=status.HTTP_400_BAD_REQUEST
            )