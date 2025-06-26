from django.core.management.base import BaseCommand
from django.utils import timezone
from reminders.models import Reminder, ReminderLog
import logging

logger = logging.getLogger('reminders')

class Command(BaseCommand):
    help = 'Limpia recordatorios antiguos y registros de log'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días de antigüedad para limpiar recordatorios (default: 30)',
        )
        parser.add_argument(
            '--log-days',
            type=int,
            default=60,
            help='Días de antigüedad para limpiar logs (default: 60)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simular la limpieza sin eliminar realmente',
        )

    def handle(self, *args, **options):
        days = options['days']
        log_days = options['log_days']
        dry_run = options['dry_run']

        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        log_cutoff_date = timezone.now() - timezone.timedelta(days=log_days)

        # Recordatorios a limpiar
        reminders_to_clean = Reminder.objects.filter(
            status__in=['completed', 'cancelled', 'failed'],
            updated_at__lt=cutoff_date
        )

        # Logs a limpiar
        logs_to_clean = ReminderLog.objects.filter(
            timestamp__lt=log_cutoff_date
        )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'🔍 Simulando limpieza de:\n'
                    f'- {reminders_to_clean.count()} recordatorios antiguos\n'
                    f'- {logs_to_clean.count()} registros de log'
                )
            )
            return

        # Limpiar recordatorios
        reminders_count = reminders_to_clean.count()
        reminders_to_clean.delete()

        # Limpiar logs
        logs_count = logs_to_clean.count()
        logs_to_clean.delete()

        # Registrar limpieza
        logger.info(
            f'Limpieza completada: {reminders_count} recordatorios y {logs_count} logs eliminados'
        )

        # Resumen
        summary = f"""
📊 Resumen de limpieza:
- Recordatorios eliminados: {reminders_count}
- Logs eliminados: {logs_count}
- Fecha de corte recordatorios: {cutoff_date.strftime('%Y-%m-%d')}
- Fecha de corte logs: {log_cutoff_date.strftime('%Y-%m-%d')}
        """

        self.stdout.write(self.style.SUCCESS(summary))
