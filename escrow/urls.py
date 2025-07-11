from django.urls import path
from .views import CreateEscrowView, ReleaseEscrowView

urlpatterns = [
    path('', CreateEscrowView.as_view(), name='create-escrow'),
    path('<int:pk>/release/', ReleaseEscrowView.as_view(), name='release-escrow'),
]

