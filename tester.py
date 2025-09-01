import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

class PaystackInitPayment(APIView):
    def post(self, request):
        email = request.data.get("email")
        amount = request.data.get("amount")  # in cedis

        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        data = {
            "email": email,
            "amount": int(amount) * 100,  # convert GHS to pesewas
            "currency": "GHS",
            "callback_url": "https://yourdomain.com/api/wallet/payment/callback/"
        }

        response = requests.post("https://api.paystack.co/transaction/initialize",
                                 json=data, headers=headers)
        return Response(response.json())
