from rest_framework import generics, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Escrow
from .serializers import EscrowSerializer
from wallet.models import Wallet
from django.utils import timezone
from notifications.utils import send_email_notification

class CreateEscrowView(generics.CreateAPIView):
    serializer_class = EscrowSerializer
    permission_classes = [IsAuthenticated]



        # Prevent duplicate escrow


    def perform_create(self, serializer):
        job = serializer.validated_data['job']
        if Escrow.objects.filter(job=job).exists():
            raise serializers.ValidationError("Escrow for this job already exists.")
        amount = serializer.validated_data['amount']
        freelancer = serializer.validated_data['freelancer']

        client_wallet = Wallet.objects.get(user=self.request.user)
        if client_wallet.balance < amount:
            raise serializers.ValidationError("Insufficient balance to fund escrow.")

        client_wallet.balance -= amount
        client_wallet.save()

        escrow = serializer.save(client=self.request.user, freelancer=freelancer)

        # Notify client and freelancer
        send_email_notification("Escrow Created", f"Escrow for job '{job.title}' has been funded.", [self.request.user.email, freelancer.email])

class ReleaseEscrowView(generics.UpdateAPIView):
    queryset = Escrow.objects.all()
    serializer_class = EscrowSerializer
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        escrow = self.get_object()
        if escrow.client != request.user:
            return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        if escrow.is_released:
            return Response({"error": "Escrow already released"}, status=status.HTTP_400_BAD_REQUEST)

        freelancer_wallet = Wallet.objects.get(user=escrow.freelancer)
        freelancer_wallet.balance += escrow.amount
        freelancer_wallet.save()

        escrow.is_released = True
        escrow.released_at = timezone.now()
        escrow.save()

        # Notify freelancer of release
        send_email_notification("Escrow Released", f"Payment for job '{escrow.job.title}' has been released.", [escrow.freelancer.email])

        return Response({"message": "Escrow released to freelancer."})