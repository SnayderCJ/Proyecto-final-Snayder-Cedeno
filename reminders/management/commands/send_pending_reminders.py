from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from reminders.models import Reminder, ReminderLog, ReminderConfiguration
from reminders.services.gmail_service import gmail_service
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Envía los recordatorios pendientes programados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin enviar recordatorios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        now = timezone.now()

        self.stdout.write(f"🔍 Buscando recordatorios pendientes... ({now.strftime('%Y-%m-%d %H:%M:%S')})")

        # Obtener recordatorios pendientes que deben enviarse
        pending_reminders = Reminder.objects.filter(
            Q(status='pending') &
            Q(scheduled_send_time__lte=now) &
            Q(target_datetime__gt=now)  # Solo enviar si aún no ha pasado la fecha objetivo
        ).select_related('user', 'user__reminder_config')

        if not pending_reminders.exists():
            self.stdout.write("✨ No hay recordatorios pendientes para enviar")
            return

        self.stdout.write(f"📬 Encontrados {pending_reminders.count()} recordatorios pendientes")

        for reminder in pending_reminders:
            try:
                # Obtener o crear configuración del usuario
                user_config, created = ReminderConfiguration.objects.get_or_create(
                    user=reminder.user,
                    defaults={
                        'reminders_enabled': True,
                        'email_enabled': True,
                        'calendar_enabled': True
                    }
                )
                
                if created:
                    self.stdout.write(f"⚙️ Creada nueva configuración para {reminder.user.username}")
                
                # Verificar si los recordatorios están habilitados para el usuario
                if not getattr(user_config, 'reminders_enabled', True):
                    self.stdout.write(f"⏭️ Saltando recordatorio {reminder.id}: recordatorios deshabilitados para {reminder.user.username}")
                    continue

                # Verificar la frecuencia adaptativa
                if user_config.adaptive_frequency:
                    if user_config.current_frequency == 'disabled':
                        self.stdout.write(f"⏭️ Saltando recordatorio {reminder.id}: frecuencia deshabilitada para {reminder.user.username}")
                        continue
                    elif user_config.current_frequency == 'low' and reminder.timing not in ['1_day', '3_days']:
                        self.stdout.write(f"⏭️ Saltando recordatorio {reminder.id}: frecuencia baja - solo recordatorios diarios")
                        continue
                    elif user_config.current_frequency == 'medium' and reminder.timing == 'immediate':
                        self.stdout.write(f"⏭️ Saltando recordatorio {reminder.id}: frecuencia media - no inmediatos")
                        continue

                self.stdout.write(f"📤 Procesando recordatorio: {reminder.title} ({reminder.id})")

                if dry_run:
                    self.stdout.write(f"🔸 [DRY RUN] Se enviaría recordatorio a {reminder.user.email}")
                    continue

                # Determinar si crear evento de calendario
                create_calendar = (
                    user_config.calendar_enabled and 
                    reminder.reminder_type in ['calendar', 'both']
                )

                # Enviar recordatorio
                result = gmail_service.send_reminder_email_with_calendar(
                    reminder=reminder,
                    create_calendar_event=create_calendar
                )

                if result['success']:
                    reminder.mark_as_sent()
                    self.stdout.write(self.style.SUCCESS(f"✅ Recordatorio enviado: {reminder.title}"))
                    
                    ReminderLog.log_action(
                        reminder=reminder,
                        action='auto_send_success',
                        details=f"Recordatorio enviado automáticamente"
                    )
                else:
                    error_msg = result.get('error', 'Error desconocido')
                    self.stdout.write(self.style.ERROR(f"❌ Error al enviar recordatorio {reminder.id}: {error_msg}"))
                    
                    reminder.send_attempts += 1
                    reminder.last_error = error_msg
                    if reminder.send_attempts >= 3:
                        reminder.status = 'failed'
                    reminder.save()
                    
                    ReminderLog.log_action(
                        reminder=reminder,
                        action='auto_send_error',
                        details=f"Error al enviar: {error_msg}",
                        success=False,
                        error_message=error_msg
                    )

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error procesando recordatorio {reminder.id}: {str(e)}"))
                logger.error(f"Error procesando recordatorio {reminder.id}: {str(e)}", exc_info=True)
                
                try:
                    ReminderLog.log_action(
                        reminder=reminder,
                        action='auto_send_error',
                        details=f"Error inesperado: {str(e)}",
                        success=False,
                        error_message=str(e)
                    )
                except:
                    pass

        self.stdout.write(self.style.SUCCESS("✅ Proceso de envío completado"))
