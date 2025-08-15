from django.urls import path
from .views import MyProfileView, MyProfileUpdateView, PublicProfileView

urlpatterns = [
    path('me/', MyProfileView.as_view(), name='my-profile'),
    path('me/update/', MyProfileUpdateView.as_view(), name='update-profile'),
    path('<user__email>/', PublicProfileView.as_view(), name='public-profile'),
]
