from rest_framework import generics, permissions
from .models import Message
from .serializers import MessageSerializer


class MessageListCreateView(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        messages = Message.objects.filter(
            sender=user
        ) | Message.objects.filter(
            recipient=user
        )
        # Mark incoming messages as read
        messages.filter(recipient=user, is_read=False).update(is_read=True)
        return messages.order_by('timestamp')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)



