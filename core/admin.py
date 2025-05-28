# core/admin.py
from django.contrib import admin
from .models import UserSettings

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'timezone']
    list_filter = ['language', 'timezone']
    search_fields = ['user__username', 'user__email']