# reminders/apps.py
from django.apps import AppConfig

class RemindersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'reminders'
    verbose_name = 'Sistema de Recordatorios'
    
    def ready(self):
        import reminders.signals