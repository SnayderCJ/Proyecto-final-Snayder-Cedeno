# core/admin.py
from django.contrib import admin
from .models import UserSettings, PasswordSetupToken, UserProfile

@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'language', 'timezone']
    list_filter = ['language', 'timezone']
    search_fields = ['user__username', 'user__email']

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'has_avatar', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_avatar(self, obj):
        return bool(obj.avatar)
    has_avatar.boolean = True
    has_avatar.short_description = 'Tiene Avatar'

@admin.register(PasswordSetupToken)
class PasswordSetupTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'token_type', 'created_at', 'expires_at', 'is_used']
    list_filter = ['token_type', 'is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'expires_at', 'used_at']
    
    def has_add_permission(self, request):
        # Prevenir creación manual de tokens desde el admin
        return False
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')