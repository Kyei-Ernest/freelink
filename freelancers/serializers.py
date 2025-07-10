from rest_framework import serializers
from .models import FreelancerProfile, Skill

class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']

class FreelancerProfileSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)

    class Meta:
        model = FreelancerProfile
        fields = ['bio', 'skills', 'campus_verified']

class FreelancerProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FreelancerProfile
        fields = ['bio', 'skills', 'student_id_card']

    def update(self, instance, validated_data):
        skills_data = validated_data.pop('skills', None)
        instance = super().update(instance, validated_data)
        if skills_data is not None:
            instance.skills.set(skills_data)
        return instance