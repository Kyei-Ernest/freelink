from django.urls import path
from .views import CampusServiceListCreateView

urlpatterns = [
    path('', CampusServiceListCreateView.as_view(), name='campus-services'),
]