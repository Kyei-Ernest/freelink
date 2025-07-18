from rest_framework.serializers import ModelSerializer
from .models import Wallet


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

