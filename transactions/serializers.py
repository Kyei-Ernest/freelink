from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, CharField, ValidationError
from .models import Transaction
from wallet.models import Wallet

class TransactionSerializer(ModelSerializer):
    client_username = serializers.CharField(source='client.username', read_only=True)
    freelancer_username = serializers.CharField(source='freelancer.username', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'client', 'freelancer', 'client_username', 'freelancer_username', 'amount', 'description', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'client', 'status', 'created_at', 'updated_at']


class TransactionStatusSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['status']
        read_only_fields = ['client', 'freelancer', 'amount', 'description', 'created_at', 'updated_at']

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Transaction._meta.get_field('status').choices]
        if value not in valid_statuses:
            raise ValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return value

    def validate(self, data):
        transaction = self.instance
        client_profile = transaction.client.client_profile
        budget_range = client_profile.budget_range
        amount = transaction.amount
        if budget_range == 'LOW' and amount > 5000:
            raise ValidationError(f"Transaction amount {amount} exceeds client's LOW budget range ($0 - $5,000)")
        elif budget_range == 'MEDIUM' and amount > 20000:
            raise ValidationError(f"Transaction amount {amount} exceeds client's MEDIUM budget range ($5,001 - $20,000)")
        if transaction.status in ['COMPLETED', 'REFUNDED'] and data['status'] in ['PENDING', 'FAILED']:
            raise ValidationError(f"Cannot change status from {transaction.status} to {data['status']}")
        return data
