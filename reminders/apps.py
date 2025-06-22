from django.apps import AppConfig


class RemindersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reminders"
    verbose_name = "Sistema de Recordatorios"

    def ready(self):
        """Importar señales cuando la app esté lista"""
        try:
            import reminders.signals  # noqa
        except ImportError:
            pass
