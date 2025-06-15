# reminders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import ReminderConfiguration

@receiver(post_save, sender=User)
def create_reminder_config(sender, instance, created, **kwargs):
    """Crear configuración de recordatorios cuando se crea un usuario"""
    if created:
        ReminderConfiguration.objects.create(
            user=instance,
            reminders_enabled=True,
            email_enabled=True,
            calendar_enabled=True
        )