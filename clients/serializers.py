from rest_framework.serializers import ModelSerializer
from .models import ClientProfile

class ClientProfileSerializer(ModelSerializer):
    class Meta:
        model = ClientProfile
        fields = ['company_name', 'industry', 'project_types', 'budget_range', 'preferred_communication']
        read_only_fields = ['user']