# reminders/admin.py
from django.contrib import admin
from .models import ReminderConfiguration, Reminder, ReminderLog

@admin.register(ReminderConfiguration)
class ReminderConfigurationAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'reminders_enabled', 'preferred_type', 
        'current_frequency', 'consecutive_ignored'
    ]
    list_filter = [
        'reminders_enabled', 'preferred_type', 'current_frequency', 
        'adaptive_frequency', 'email_enabled', 'calendar_enabled'
    ]
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at', 'last_adaptation']
    
    fieldsets = (
        ('Información del Usuario', {
            'fields': ('user',)
        }),
        ('Configuración General', {
            'fields': (
                'reminders_enabled', 'preferred_type', 'default_timing'
            )
        }),
        ('Frecuencia Adaptativa', {
            'fields': (
                'adaptive_frequency', 'current_frequency', 
                'consecutive_ignored', 'last_adaptation'
            )
        }),
        ('Preferencias de Canales', {
            'fields': ('email_enabled', 'calendar_enabled')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'user', 'target_datetime', 'status', 
        'reminder_type', 'responded', 'send_attempts'
    ]
    list_filter = [
        'status', 'reminder_type', 'timing', 'responded', 
        'created_at', 'target_datetime'
    ]
    search_fields = ['title', 'user__username', 'description']
    date_hierarchy = 'target_datetime'
    readonly_fields = [
        'id', 'created_at', 'updated_at', 'actual_send_time', 
        'response_time', 'scheduled_send_time'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('id', 'user', 'title', 'description')
        }),
        ('Programación', {
            'fields': (
                'target_datetime', 'reminder_type', 'timing', 
                'scheduled_send_time'
            )
        }),
        ('Estado', {
            'fields': (
                'status', 'send_attempts', 'last_error'
            )
        }),
        ('Respuesta del Usuario', {
            'fields': (
                'responded', 'response_time', 'response_action'
            )
        }),
        ('IDs de Servicios Externos', {
            'fields': ('email_message_id', 'calendar_event_id'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'actual_send_time'),
            'classes': ('collapse',)
        })
    )

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = [
        'reminder', 'action', 'success', 'timestamp'
    ]
    list_filter = ['action', 'success', 'timestamp']
    search_fields = ['reminder__title', 'action', 'details']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def has_add_permission(self, request):
        return False  # Los logs solo se crean automáticamente
    
    def has_change_permission(self, request, obj=None):
        return False  # Los logs no se pueden editar