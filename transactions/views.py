from django.db import models
from rest_framework.exceptions import ValidationError
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from django.contrib.auth import get_user_model
import logging
from .serializers import TransactionSerializer, TransactionStatusSerializer

from wallet.models import Wallet

logger = logging.getLogger(__name__)
User = get_user_model()

class TransactionView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        if not (request.user.is_client or request.user.is_freelancer):
            return Response(
                {'error': 'Only clients or freelancers can access transactions'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to access transactions'},
                status=status.HTTP_403_FORBIDDEN
            )
        transactions = Transaction.objects.filter(
            models.Q(client=request.user) | models.Q(freelancer=request.user)
        )
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        if not request.user.is_client:
            return Response(
                {'error': 'Only clients can create transactions'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to create transactions'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not hasattr(request.user, 'client_profile'):
            return Response(
                {'error': 'Client must have a profile'},
                status=status.HTTP_400_BAD_REQUEST
            )

        data = request.data.copy()
        data['client'] = request.user.id
        serializer = TransactionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"Transaction created: {serializer.data['amount']} from {request.user.username} "
                f"to {serializer.data['freelancer_username']} (Phone: {request.user.phone})"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateTransactionStatusView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def put(self, request, transaction_id):
        if not (request.user.is_client or request.user.is_staff):
            return Response(
                {'error': 'Only the client or an admin can update transaction status'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to update transactions'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            transaction = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        if request.user != transaction.client and not request.user.is_staff:
            return Response(
                {'error': 'You are not authorized to update this transaction'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TransactionStatusSerializer(transaction, data=request.data, partial=True)
        if serializer.is_valid():
            # Update wallet balances if status changes to COMPLETED
            if serializer.validated_data['status'] == 'COMPLETED' and transaction.status != 'COMPLETED':
                try:
                    client_wallet = transaction.client.wallet
                    freelancer_wallet = transaction.freelancer.wallet
                    if client_wallet.balance < transaction.amount:
                        raise ValidationError("Insufficient funds in client's wallet.")
                    client_wallet.withdraw(transaction.amount)
                    freelancer_wallet.deposit(transaction.amount)
                except Wallet.DoesNotExist:
                    return Response(
                        {'error': 'Both client and freelancer must have wallets'},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            serializer.save()
            logger.info(
                f"Transaction {transaction_id} status updated to {serializer.data['status']} "
                f"by {request.user.username} (Phone: {request.user.phone}, Role: {'Client' if request.user.is_client else 'Admin'})"
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

