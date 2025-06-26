from django.core.management.base import BaseCommand
from django.utils import timezone
from reminders.models import Reminder
from reminders.services.gmail_service import GmailService
import logging

logger = logging.getLogger("reminders")


class Command(BaseCommand):
    help = "Envía recordatorios pendientes programados"

    def handle(self, *args, **kwargs):
        now = timezone.now()
        gmail_service = GmailService()

        # Obtener recordatorios pendientes que deben enviarse
        pending_reminders = Reminder.objects.filter(
            status="pending", scheduled_send_time__lte=now
        ).select_related("user")

        self.stdout.write(
            f"Encontrados {pending_reminders.count()} recordatorios pendientes"
        )

        for reminder in pending_reminders:
            try:
                # Verificar configuración del usuario
                if not reminder.user.reminder_config.reminders_enabled:
                    reminder.mark_as_cancelled()
                    logger.info(
                        f"Recordatorio {reminder.id} cancelado - recordatorios desactivados para el usuario"
                    )
                    continue

                # Enviar recordatorio
                result = gmail_service.send_reminder_email_with_calendar(reminder)

                if result.get("success"):
                    reminder.mark_as_sent()
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Recordatorio {reminder.id} enviado exitosamente a {reminder.user.email}"
                        )
                    )
                else:
                    reminder.mark_as_failed(result.get("error"))
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error enviando recordatorio {reminder.id}: {result.get('error')}"
                        )
                    )

            except Exception as e:
                error_msg = f"Error procesando recordatorio {reminder.id}: {str(e)}"
                logger.error(error_msg)
                reminder.mark_as_failed(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

        self.stdout.write(
            self.style.SUCCESS("Proceso de envío de recordatorios completado")
        )
