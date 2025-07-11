from django.contrib import admin
from .models import FreelancerProfile, Skill

admin.site.register(Skill)

@admin.register(FreelancerProfile)
class FreelancerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'campus_verified')
