from django.contrib import admin
from .models import FreelancerProfile

@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'availability', 'hourly_rate', 'created_at')
    list_filter = ('availability', 'created_at')
    search_fields = ('user__username', 'user__phone', 'skills')

    def phone(self, obj):
        return obj.user.phone