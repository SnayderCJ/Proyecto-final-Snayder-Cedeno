from django.contrib import admin
from .models import Reminder, ReminderConfig, ReminderLog


@admin.register(ReminderConfig)
class ReminderConfigAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "reminders_enabled",
        "email_enabled",
        "calendar_enabled",
        "preferred_type",
        "current_frequency",
    ]
    list_filter = [
        "reminders_enabled",
        "email_enabled",
        "calendar_enabled",
        "preferred_type",
        "current_frequency",
    ]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    readonly_fields = ["created_at", "updated_at"]


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "user",
        "target_datetime",
        "status",
        "reminder_type",
        "send_attempts",
        "created_at",
    ]
    list_filter = ["status", "reminder_type", "timing", "created_at"]
    search_fields = ["title", "description", "user__email"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "scheduled_send_time",
        "last_attempt",
    ]
    date_hierarchy = "target_datetime"

    fieldsets = (
        (
            "Información Básica",
            {"fields": ("user", "title", "description", "target_datetime")},
        ),
        ("Configuración", {"fields": ("reminder_type", "timing", "status")}),
        (
            "Seguimiento",
            {
                "fields": ("send_attempts", "last_attempt", "last_error"),
                "classes": ("collapse",),
            },
        ),
        (
            "IA Generada",
            {"fields": ("ai_subject", "ai_description"), "classes": ("collapse",)},
        ),
        (
            "Metadatos",
            {
                "fields": ("created_at", "updated_at", "scheduled_send_time"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ["reminder", "action", "success", "timestamp"]
    list_filter = ["action", "success", "timestamp"]
    search_fields = ["reminder__title", "action", "details"]
    readonly_fields = ["timestamp"]
    date_hierarchy = "timestamp"
