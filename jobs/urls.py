from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'skills', views.SkillViewSet, basename='skill')

urlpatterns = [
    path('', views.JobListCreateView.as_view(), name='job-list-create'),
    path('<int:pk>/', views.JobRetrieveUpdateDestroyView.as_view(), name='job-detail'),
    path('<int:pk>/status/', views.JobUpdateStatusView.as_view(), name='job-update-status'),

    # Include router URLs
    path('', include(router.urls)),
]




