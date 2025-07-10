from django.urls import path
from .views import FreelancerProfileView, UpdateFreelancerProfileView, SkillListView

urlpatterns = [
    path('me/', FreelancerProfileView.as_view(), name='freelancer-profile'),
    path('me/update/', UpdateFreelancerProfileView.as_view(), name='freelancer-update'),
    path('skills/', SkillListView.as_view(), name='skill-list'),
]