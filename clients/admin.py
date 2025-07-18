from django.contrib import admin
from .models import ClientProfile

@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'company_name', 'industry', 'budget_range', 'created_at')
    list_filter = ('budget_range', 'preferred_communication', 'created_at')
    search_fields = ('user__username', 'user__phone', 'company_name', 'industry')

    def phone(self, obj):
        return obj.user.phone