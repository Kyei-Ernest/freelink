from rest_framework.serializers import ModelSerializer
from .models import Wallet, Currency


class WalletSerializer(ModelSerializer):
    class Meta:
        model = Wallet
        fields = [
            "id",
            "user",
            "currency",
            "balance",
            "available_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "balance",
            "currency",
            "available_balance",
            "created_at",
            "updated_at",
            "user",   # user is set automatically
        ]


class CurrencySerializer(ModelSerializer):
    class Meta:
        model = Currency
        fields = "__all__"
