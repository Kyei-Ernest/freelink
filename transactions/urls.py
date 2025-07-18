from django.urls import path
from .views import TransactionView, UpdateTransactionStatusView

urlpatterns = [
    path('', TransactionView.as_view(), name='transactions'),
    path('<int:transaction_id>/status/', UpdateTransactionStatusView.as_view(), name='update-transaction-status'),
]