from rest_framework import generics, permissions
from .models import ClientProfile
from .serializers import ClientProfileSerializer
from rest_framework.exceptions import NotFound

class ClientProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ClientProfileSerializer
    permission_classes = [permissions.IsAuthenticated]


    def get_object(self):
        try:
            return ClientProfile.objects.get(user=self.request.user)
        except ClientProfile.DoesNotExist:
            raise NotFound('Client profile not found.')
