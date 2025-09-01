import requests
from django.conf import settings
from rest_framework.views import APIView
from .models import Payment
import uuid
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Withdrawal
from .serializers import  DepositSerializer
from wallet.models import Wallet
from .services.paystack import create_transfer_recipient, initiate_transfer



class InitPaymentView(APIView):
    serializer_class = DepositSerializer

    def post(self, request):
        user = request.user
        amount = int(request.data.get("amount")) * 100  # GHS → pesewas
        reference = str(uuid.uuid4()).replace("-", "")[:12]  # unique reference

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": user.email,
            "amount": amount,
            "currency": "GHS",
            "reference": reference,
            "callback_url": "http://127.0.0.1:8000/api/payments/verify/",
        }

        r = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
        res = r.json()

        if res.get("status"):
            payment = Payment.objects.create(user=user, amount=amount, reference=reference)
            return Response(res, status=status.HTTP_200_OK)
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


class VerifyPaymentView(APIView):
    def get(self, request):
        reference = request.query_params.get("reference")

        headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        r = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
        res = r.json()

        try:
            payment = Payment.objects.get(reference=reference)
        except Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        if res["data"]["status"] == "success":
            payment.status = "success"
            payment.save()
        else:
            payment.status = "failed"
            payment.save()

        return Response(res, status=status.HTTP_200_OK)



"""class WithdrawalCreateView(generics.CreateAPIView):
    serializer_class = WithdrawalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        wallet = self.request.user.wallet
        amount = serializer.validated_data["amount"]

        if amount > wallet.balance:
            raise ValueError("Insufficient balance")

        # Deduct from wallet first
        wallet.balance -= amount
        wallet.save()

        reference = str(uuid.uuid4())

        # Create Paystack recipient
        recipient_code = create_transfer_recipient(
            name=serializer.validated_data["account_name"],
            account_number=serializer.validated_data["account_number"],
            bank_code=serializer.validated_data["bank_code"]
        )

        # Initiate Paystack transfer
        transfer_data = initiate_transfer(amount, recipient_code, reference)

        serializer.save(
            user=self.request.user,
            reference=reference,
            status="processing",
            paystack_transfer_code=transfer_data["transfer_code"]
        )


from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import hmac, hashlib

@csrf_exempt
@api_view(["POST"])
def paystack_webhook(request):
    secret = settings.PAYSTACK_SECRET_KEY.encode()
    signature = request.headers.get("x-paystack-signature")

    computed_sig = hmac.new(secret, request.body, hashlib.sha512).hexdigest()
    if signature != computed_sig:
        return JsonResponse({"error": "Invalid signature"}, status=400)

    event = request.data
    if event["event"] == "transfer.success":
        Withdrawal.objects.filter(reference=event["data"]["reference"]).update(status="successful")
    elif event["event"] == "transfer.failed":
        Withdrawal.objects.filter(reference=event["data"]["reference"]).update(status="failed")

    return JsonResponse({"status": "ok"})
"""