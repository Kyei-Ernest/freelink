from django.contrib import admin
from django.urls import path,include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/users/', include('users.urls')),
    path('api/freelancers/', include('freelancers.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/jobs/', include('jobs.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/ratings/', include('ratings.urls')),
    path('api/campus/', include('campus.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/escrow/', include('escrow.urls')),
    path('api/wallet/', include('wallet.urls')),
]


