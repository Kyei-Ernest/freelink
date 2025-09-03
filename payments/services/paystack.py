import uuid
from decimal import Decimal
import requests
from django.conf import settings
from payments.models import Payment
from wallet.models import Wallet


BASE_URL = "https://api.paystack.co"


def create_transfer_recipient(name, account_number, service_provider):
    url = f"{BASE_URL}/transferrecipient"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET}",
        "Content-Type": "application/json",
    }
    payload = {
        "type": "mobile_money",
        "name": name,
        "account_number": account_number,
        "bank_code": service_provider,  # e.g. MTN, Vodafone, AirtelTigo codes
        "currency": "GHS",
    }

    res = requests.post(url, json=payload, headers=headers)
    try:
        res.raise_for_status()
    except Exception:
        print("Paystack Recipient Error:", res.json())
        raise

    return res.json()["data"]["recipient_code"]


def initiate_transfer(amount, recipient_code, reference):
    url = f"{BASE_URL}/transfer"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET}",
        "Content-Type": "application/json",
    }
    data = {
        "source": "balance",
        "amount": int(float(amount) * 100),  # GHS → pesewas
        "recipient": recipient_code,
        "reference": reference,
        "reason": "User Withdrawal",
    }

    res = requests.post(url, json=data, headers=headers)
    try:
        res.raise_for_status()
    except Exception:
        print("Paystack Transfer Error:", res.json())
        raise

    return res.json()

def initialize_payment(user, amount):
    """Initialize a Paystack payment and return response data."""

    # Convert amount GHS → pesewas
    amount_in_pesewas = int(amount) * 100
    reference = str(uuid.uuid4()).replace("-", "")[:12]

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": user.email,
        "amount": amount_in_pesewas,
        "currency": "GHS",
        "reference": reference,
        "callback_url": "http://127.0.0.1:8000/api/payments/verify/",
    }

    r = requests.post("https://api.paystack.co/transaction/initialize", json=data, headers=headers)
    res = r.json()

    if res.get("status"):
        # save payment record in DB
        Payment.objects.create(user=user, amount=Decimal(amount), reference=reference)

    return res


def verify_payment(reference):
    """Verify a Paystack payment and update records accordingly."""
    headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
    r = requests.get(f"https://api.paystack.co/transaction/verify/{reference}", headers=headers)
    res = r.json()

    try:
        payment = Payment.objects.get(reference=reference)
    except Payment.DoesNotExist:
        return {"error": "Payment not found", "status_code": 404}

    if res["data"]["status"] == "success":
        # Mark payment successful
        payment.status = "success"
        payment.save()

        # Credit wallet
        wallet, _ = Wallet.objects.get_or_create(user=payment.user)
        wallet.balance += Decimal(res["data"]["amount"]) / Decimal(100)
        wallet.save()
    else:
        # Mark payment failed
        payment.status = "failed"
        payment.save()

    return {"response": res, "status_code": 200}
