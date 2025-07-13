from rest_framework import serializers
from .models import Job, JobApplication

class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['client', 'created_at']

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['freelancer', 'applied_at']

class JobCompletionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = ['status']
        read_only_fields = ['status']