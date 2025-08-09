from rest_framework import serializers
from .models import Escrow


class EscrowSerializer(serializers.ModelSerializer):
    transaction_id = serializers.IntegerField(source='transaction.id', read_only=True)

    class Meta:
        model = Escrow
        fields = ['transaction_id', 'amount', 'status', 'created_at', 'updated_at']
        read_only_fields = ['transaction_id', 'amount', 'created_at', 'updated_at']