from .views import WalletView, CurrencyViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register("currencies", CurrencyViewSet, basename="currency")

urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet'),
    path("", include(router.urls)),

]

