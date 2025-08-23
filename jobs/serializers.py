from rest_framework import serializers
from .models import Job, Skill


class JobSerializer(serializers.ModelSerializer):
    client = serializers.StringRelatedField(read_only=True)  # Show client's username/name
    freelancer = serializers.StringRelatedField(read_only=True)  # Show freelancer's username/name
    skills_required = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Skill.objects.all(),
        required=False
    )

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('client', 'freelancer', 'status', 'created_at', 'updated_at')  # Set in views


    def create(self, validated_data):
        skills = validated_data.pop("skills_required", [])
        job = Job.objects.create(**validated_data)

        for skill_name in skills:
            normalized = skill_name.name.strip().title()
            # First, try to find case-insensitive match
            skill = Skill.objects.filter(name__iexact=normalized).first()
            if not skill:
                # Create if it doesn't exist
                skill = Skill.objects.create(name=normalized, approved=False)

            job.skills_required.add(skill)

        return job

class JobDetailSerializer(JobSerializer):
    """
    Detailed serializer for a single job.
    Can be extended to include proposals, client profile, freelancer profile, etc.
    """
    client = serializers.StringRelatedField(read_only=True)
    freelancer = serializers.StringRelatedField(read_only=True)

    class Meta(JobSerializer.Meta):
        fields = JobSerializer.Meta.fields


class JobStatusSerializer(serializers.ModelSerializer):
    """
    Separate serializer for updating only the job status.
    Useful for endpoints like: /jobs/<id>/update-status/
    """
    class Meta:
        model = Job
        fields = ('status',)

class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model (used by admins)."""

    class Meta:
        model = Skill
        fields = ["id", "name"]

    def validate_name(self, value):
        # Normalize first (all lowercase, strip spaces)
        normalized = value.strip().lower()

        # Check if skill with same name exists (case-insensitive)
        if Skill.objects.filter(name__iexact=normalized).exists():
            raise serializers.ValidationError("This skill already exists.")

        # Return normalized (or formatted) value
        return normalized
