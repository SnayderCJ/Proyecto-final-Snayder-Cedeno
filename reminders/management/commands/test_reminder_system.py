from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from reminders.models import Reminder, ReminderConfig
from reminders.services.gmail_service import GmailService
import logging

User = get_user_model()
logger = logging.getLogger("reminders")


class Command(BaseCommand):
    help = "Prueba el sistema de recordatorios"

    def add_arguments(self, parser):
        parser.add_argument(
            "--user", type=str, help="Email del usuario para la prueba", required=True
        )
        parser.add_argument(
            "--skip-email", action="store_true", help="Omitir envío de email de prueba"
        )

    def handle(self, *args, **kwargs):
        user_email = kwargs["user"]
        skip_email = kwargs["skip_email"]

        try:
            # Buscar usuario
            user = User.objects.get(email=user_email)
            self.stdout.write(f"Usuario encontrado: {user.email}")

            # Verificar o crear configuración de recordatorios
            config, created = ReminderConfig.objects.get_or_create(user=user)
            if created:
                self.stdout.write("Configuración de recordatorios creada")
            else:
                self.stdout.write("Configuración de recordatorios existente")

            # Mostrar estado de configuración
            self.stdout.write(f"Recordatorios habilitados: {config.reminders_enabled}")
            self.stdout.write(f"Email habilitado: {config.email_enabled}")
            self.stdout.write(f"Calendario habilitado: {config.calendar_enabled}")

            if not skip_email:
                # Probar servicio de email
                gmail_service = GmailService()
                result = gmail_service.send_test_email(user)

                if result.get("success"):
                    self.stdout.write(
                        self.style.SUCCESS("✅ Email de prueba enviado exitosamente")
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"❌ Error enviando email: {result.get('error')}"
                        )
                    )

            # Crear recordatorio de prueba
            test_reminder = Reminder.objects.create(
                user=user,
                title="🧪 Recordatorio de Prueba del Sistema",
                description="Este es un recordatorio de prueba para verificar el funcionamiento del sistema.",
                target_datetime=timezone.now() + timezone.timedelta(minutes=1),
                reminder_type="email",
                timing="immediate",
                ai_subject="🧪 PRUEBA - Sistema de Recordatorios Funcionando",
                ai_description="<p>¡Excelente! El sistema de recordatorios está funcionando correctamente.</p>",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ Recordatorio de prueba creado con ID: {test_reminder.id}"
                )
            )

            # Mostrar información del recordatorio
            self.stdout.write(f"Título: {test_reminder.title}")
            self.stdout.write(f"Programado para: {test_reminder.scheduled_send_time}")
            self.stdout.write(f"Estado: {test_reminder.get_status_display()}")

            self.stdout.write(
                self.style.SUCCESS(
                    "\n🎉 Sistema de recordatorios probado exitosamente!"
                )
            )
            self.stdout.write("Para enviar recordatorios pendientes, ejecuta:")
            self.stdout.write("python manage.py send_pending_reminders")

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"❌ Usuario con email {user_email} no encontrado")
            )
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error durante la prueba: {str(e)}"))
            logger.error(f"Error en test_reminder_system: {str(e)}")
