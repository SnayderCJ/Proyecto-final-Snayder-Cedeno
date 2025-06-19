from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from reminders.models import Reminder, ReminderLog

class Command(BaseCommand):
    help = 'Limpia recordatorios vencidos y logs antiguos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días de antigüedad para limpiar recordatorios completados (default: 30)',
        )
        parser.add_argument(
            '--log-days',
            type=int,
            default=90,
            help='Días de antigüedad para limpiar logs (default: 90)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin eliminar datos',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days = options['days']
        log_days = options['log_days']
        now = timezone.now()

        self.stdout.write(f"🧹 Iniciando limpieza de recordatorios... ({now.strftime('%Y-%m-%d %H:%M:%S')})")

        # 1. Marcar recordatorios vencidos como fallidos
        expired_reminders = Reminder.objects.filter(
            status='pending',
            target_datetime__lt=now - timedelta(hours=1)  # 1 hora de gracia
        )

        if expired_reminders.exists():
            count = expired_reminders.count()
            self.stdout.write(f"⏰ Encontrados {count} recordatorios vencidos")
            
            if not dry_run:
                expired_reminders.update(status='failed', last_error='Recordatorio vencido')
                self.stdout.write(f"✅ Marcados {count} recordatorios como fallidos")
            else:
                self.stdout.write(f"🔸 [DRY RUN] Se marcarían {count} recordatorios como fallidos")

        # 2. Limpiar recordatorios completados antiguos
        old_completed = Reminder.objects.filter(
            status__in=['completed', 'cancelled'],
            updated_at__lt=now - timedelta(days=days)
        )

        if old_completed.exists():
            count = old_completed.count()
            self.stdout.write(f"📦 Encontrados {count} recordatorios completados antiguos (>{days} días)")
            
            if not dry_run:
                old_completed.delete()
                self.stdout.write(f"🗑️ Eliminados {count} recordatorios antiguos")
            else:
                self.stdout.write(f"🔸 [DRY RUN] Se eliminarían {count} recordatorios antiguos")

        # 3. Limpiar logs antiguos
        old_logs = ReminderLog.objects.filter(
            timestamp__lt=now - timedelta(days=log_days)
        )

        if old_logs.exists():
            count = old_logs.count()
            self.stdout.write(f"📋 Encontrados {count} logs antiguos (>{log_days} días)")
            
            if not dry_run:
                old_logs.delete()
                self.stdout.write(f"🗑️ Eliminados {count} logs antiguos")
            else:
                self.stdout.write(f"🔸 [DRY RUN] Se eliminarían {count} logs antiguos")

        # 4. Estadísticas finales
        total_reminders = Reminder.objects.count()
        pending_reminders = Reminder.objects.filter(status='pending').count()
        total_logs = ReminderLog.objects.count()

        self.stdout.write(f"\n📊 Estadísticas actuales:")
        self.stdout.write(f"   📋 Total recordatorios: {total_reminders}")
        self.stdout.write(f"   ⏳ Pendientes: {pending_reminders}")
        self.stdout.write(f"   📝 Total logs: {total_logs}")

        self.stdout.write(self.style.SUCCESS("✅ Limpieza completada"))
