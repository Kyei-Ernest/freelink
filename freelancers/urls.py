from django.urls import path
from .views import FreelancerProfileView

urlpatterns = [
    path('profile/', FreelancerProfileView.as_view(), name='freelancer-profile'),
]