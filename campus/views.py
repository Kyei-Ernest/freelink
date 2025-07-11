from rest_framework import generics
from .models import CampusService
from .serializers import CampusServiceSerializer

class CampusServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = CampusServiceSerializer

    def get_queryset(self):
        return CampusService.objects.all()

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)
