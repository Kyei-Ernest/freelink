from django.urls import path
from .views import InitPaymentView, VerifyPaymentView, InitiateTransferView, CreateTransferRecipientView

urlpatterns = [
    path("init/", InitPaymentView.as_view(), name="init-payment"),
    path("verify/", VerifyPaymentView.as_view(), name="verify-payment"),
    path("transfer/", InitiateTransferView.as_view(), name="init-transfer" ),
    path("create_transfer_recipient/", CreateTransferRecipientView.as_view(), name="create-transfer-recipient")
]
