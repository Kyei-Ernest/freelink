from django.urls import path
from .views import ClientProfileView

urlpatterns = [
    path('profile/', ClientProfileView.as_view(), name='client-profile'),]