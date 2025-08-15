from rest_framework import generics, permissions
from .serializers import MessageSerializer

class SendMessageView(generics.CreateAPIView):
    """
    API endpoint to send a new message.
    The sender is always the current logged-in user.
    The recipient username is provided manually in the request.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]


class InboxView(generics.ListAPIView):
    """
    API endpoint to list all messages received by the logged-in user.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(recipient__username=self.request.user.username)


class SentMessagesView(generics.ListAPIView):
    """
    API endpoint to list all messages sent by the logged-in user.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


from rest_framework import generics, permissions
from django.db.models import Q
from .models import Message
from .serializers import MessageSerializer

class MessageDetailView(generics.ListAPIView):
    """List all messages between the logged-in user and the given username.
    Marks as read if recipient is current viewer.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        username = self.kwargs['username']
        current_user = self.request.user

        queryset = Message.objects.filter(
            Q(sender__username=current_user.username, recipient__username=username) |
            Q(sender__username=username, recipient__username=current_user.username)
        ).order_by('created_at')

        # Mark as read for all messages where current user is recipient
        queryset.filter(
            recipient__username=current_user.username,
            is_read=False
        ).update(is_read=True)

        return queryset

