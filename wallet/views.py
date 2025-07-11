from rest_framework import generics, permissions, serializers
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer

class WalletDetailView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Wallet.objects.get(user=self.request.user)

class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(wallet__user=self.request.user)

    def perform_create(self, serializer):
        wallet = Wallet.objects.get(user=self.request.user)
        data = serializer.validated_data
        amount = data['amount']
        if data['type'] == 'DEBIT' and wallet.balance < amount:
            raise serializers.ValidationError("Insufficient balance.")

        if data['type'] == 'CREDIT':
            wallet.balance += amount
        else:
            wallet.balance -= amount
        wallet.save()

        serializer.save(wallet=wallet)