from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')
