from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound

from .models import FreelancerProfile, Skill
from .serializers import FreelancerProfileSerializer, FreelancerProfileUpdateSerializer, SkillSerializer

class FreelancerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FreelancerProfileSerializer

    def get_object(self):
        return FreelancerProfile.objects.get(user=self.request.user)

class UpdateFreelancerProfileView(generics.UpdateAPIView):
    serializer_class = FreelancerProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        try:
            return FreelancerProfile.objects.get(user=self.request.user)
        except FreelancerProfile.DoesNotExist:
            raise NotFound("Freelancer profile not found.")

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]