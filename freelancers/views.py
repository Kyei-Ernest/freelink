from rest_framework import generics, permissions
from .models import FreelancerProfile, Skill
from .serializers import FreelancerProfileSerializer, FreelancerProfileUpdateSerializer, SkillSerializer

class FreelancerProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = FreelancerProfileSerializer

    def get_object(self):
        return FreelancerProfile.objects.get(user=self.request.user)

class UpdateFreelancerProfileView(generics.UpdateAPIView):
    serializer_class = FreelancerProfileUpdateSerializer

    def get_object(self):
        return FreelancerProfile.objects.get(user=self.request.user)

class SkillListView(generics.ListAPIView):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.AllowAny]