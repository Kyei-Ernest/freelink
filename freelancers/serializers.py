from rest_framework import serializers
from .models import FreelancerProfile


class FreelancerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerProfile
        fields = ['bio', 'skills', 'hourly_rate', 'portfolio_url', 'availability']
        read_only_fields = ['user']

