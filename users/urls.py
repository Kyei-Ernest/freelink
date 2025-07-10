from django.urls import path
from .views import RegisterView, ProfileView, LoginView, LogoutView, VerifyPhoneView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
]