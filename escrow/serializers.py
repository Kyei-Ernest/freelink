from rest_framework import serializers
from .models import Escrow

class EscrowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Escrow
        fields = '__all__'
        read_only_fields = ['client', 'freelancer', 'is_released', 'created_at', 'released_at', 'disputed']