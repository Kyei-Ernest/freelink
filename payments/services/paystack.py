import requests
from django.conf import settings

PAYSTACK_SECRET = settings.PAYSTACK_SECRET_KEY
BASE_URL = "https://api.paystack.co"

def create_transfer_recipient(name, account_number, bank_code):
    url = f"{BASE_URL}/transferrecipient"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    payload = {
        "type": "nuban",   # for bank accounts (use "mobile_money" for momo wallets in Ghana)
        "name": name,
        "account_number": account_number,
        "bank_code": bank_code,
        "currency": "GHS",  # Ghana cedi
    }
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()["data"]["recipient_code"]

def initiate_transfer(amount, recipient_code, reference):
    url = f"{BASE_URL}/transfer"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET}"}
    payload = {
        "source": "balance",
        "amount": int(amount * 100),  # Paystack expects kobo/pesewas
        "recipient": recipient_code,
        "reference": reference,
        "reason": "User Withdrawal"
    }
    res = requests.post(url, json=payload, headers=headers)
    res.raise_for_status()
    return res.json()["data"]
