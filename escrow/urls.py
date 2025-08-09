from django.urls import path
from .views import EscrowView

urlpatterns = [
    path('escrow/<int:transaction_id>/', EscrowView.as_view(), name='escrow'),

]

