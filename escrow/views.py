from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from .models import Escrow
import logging

from transactions.models import Transaction

from .serializers import EscrowSerializer

logger = logging.getLogger(__name__)



class EscrowView(APIView):
    serializer_class = EscrowSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request, transaction_id):
        if not (request.user.is_client or request.user.is_freelancer or request.user.is_staff):
            return Response(
                {'error': 'Only profiles, freelancers, or admins can access escrow details'},
                status=status.HTTP_403_FORBIDDEN
            )
        if not request.user.is_verified:
            return Response(
                {'error': 'Account must be verified to access escrow'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            if request.user != transaction.client and request.user != transaction.freelancer and not request.user.is_staff:
                return Response(
                    {'error': 'You are not authorized to view this escrow'},
                    status=status.HTTP_403_FORBIDDEN
                )
            escrow = transaction.escrow
            serializer = EscrowSerializer(escrow)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response(
                {'error': 'Transaction not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Escrow.DoesNotExist:
            return Response(
                {'error': 'Escrow not found'},
                status=status.HTTP_404_NOT_FOUND
            )