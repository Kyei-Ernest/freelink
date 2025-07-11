from rest_framework import serializers
from .models import ClientProfile

class ClientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['company_name', 'company_website', 'description']