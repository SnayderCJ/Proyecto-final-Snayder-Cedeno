from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.timezone import now as timezone_now
from datetime import timedelta
from reminders.models import Reminder, ReminderConfiguration, ReminderLog
from reminders.services.gmail_service import gmail_service
import time

class Command(BaseCommand):
    help = 'Prueba completa del sistema de recordatorios automáticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            required=True,
            help='Username del usuario para la prueba',
        )
        parser.add_argument(
            '--skip-email',
            action='store_true',
            help='Saltar envío real de email',
        )

    def handle(self, *args, **options):
        username = options['user']
        skip_email = options['skip_email']

        self.stdout.write(self.style.SUCCESS('🧪 Iniciando prueba completa del sistema de recordatorios\n'))

        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'✅ Usuario encontrado: {user.username} ({user.email})')
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Usuario "{username}" no encontrado'))
            return

        # 1. Verificar/crear configuración
        self.test_user_configuration(user)

        # 2. Crear recordatorio de prueba
        reminder = self.create_test_reminder(user)

        # 3. Probar envío (si no se salta)
        if not skip_email:
            self.test_reminder_sending(reminder)

        # 4. Probar respuestas de usuario
        self.test_user_responses(reminder)

        # 5. Probar limpieza
        self.test_cleanup_system()

        # 6. Estadísticas finales
        self.show_final_stats(user)

        self.stdout.write(self.style.SUCCESS('\n✅ Prueba completa del sistema finalizada'))

    def test_user_configuration(self, user):
        self.stdout.write('\n📋 1. Probando configuración de usuario...')
        
        # Obtener o crear configuración
        config, created = ReminderConfiguration.objects.get_or_create(
            user=user,
            defaults={
                'reminders_enabled': True,
                'email_enabled': True,
                'calendar_enabled': True,
                'preferred_type': 'both',
                'default_timing': '15_min'
            }
        )

        if created:
            self.stdout.write('   ✅ Configuración creada con valores por defecto')
        else:
            self.stdout.write('   ✅ Configuración existente encontrada')

        # Mostrar configuración actual
        self.stdout.write(f'   📧 Email habilitado: {config.email_enabled}')
        self.stdout.write(f'   📅 Calendar habilitado: {config.calendar_enabled}')
        self.stdout.write(f'   🔔 Recordatorios activos: {config.reminders_enabled}')
        self.stdout.write(f'   📊 Frecuencia actual: {getattr(config, "current_frequency", "Desconocido")}')
        self.stdout.write(f'   ⏰ Tiempo por defecto: {getattr(config, "default_timing", "Desconocido")}')

        return config

    def create_test_reminder(self, user):
        self.stdout.write('\n📝 2. Creando recordatorio de prueba...')
        
        # Crear recordatorio que se envíe en 30 segundos
        target_time = timezone_now() + timedelta(minutes=2)
        
        reminder = Reminder.objects.create(
            user=user,
            title='🧪 Prueba del Sistema Automático',
            description='Este es un recordatorio de prueba creado por el comando de testing.',
            target_datetime=target_time,
            reminder_type='both',
            timing='immediate',  # Se enviará inmediatamente
            ai_subject='🧪 Sistema de Recordatorios - Prueba Exitosa',
            ai_description=f'''
            <div style="background: #d4edda; padding: 20px; border-radius: 10px;">
                <h3 style="color: #155724;">✅ ¡Prueba del Sistema Exitosa!</h3>
                <p style="color: #155724;">
                    Este recordatorio fue creado y enviado automáticamente por el sistema de testing.
                </p>
                <p style="color: #155724;">
                    <strong>Detalles de la prueba:</strong><br>
                    • Usuario: {user.username}<br>
                    • Email: {user.email}<br>
                    • Fecha de creación: {timezone_now().strftime("%d/%m/%Y %H:%M:%S")}<br>
                    • Programado para: {target_time.strftime("%d/%m/%Y %H:%M:%S")}
                </p>
            </div>
            '''
        )

        self.stdout.write(f'   ✅ Recordatorio creado: {reminder.id}')
        self.stdout.write(f'   📅 Programado para: {reminder.scheduled_send_time.strftime("%Y-%m-%d %H:%M:%S")}')
        self.stdout.write(f'   🎯 Fecha objetivo: {reminder.target_datetime.strftime("%Y-%m-%d %H:%M:%S")}')

        return reminder

    def test_reminder_sending(self, reminder):
        self.stdout.write('\n📤 3. Probando envío de recordatorio...')
        
        if not gmail_service:
            self.stdout.write('   ❌ Gmail Service no disponible')
            return False

        # Verificar que el recordatorio esté listo para enviar
        if not reminder.is_ready_to_send():
            self.stdout.write('   ⏳ Recordatorio no está listo para enviar aún')
            self.stdout.write('   🔄 Forzando envío para prueba...')

        try:
            # Obtener configuración del usuario
            config = reminder.user.reminder_config

            # Determinar si crear calendario
            create_calendar = (
                config.calendar_enabled and 
                reminder.reminder_type in ['calendar', 'both']
            )

            self.stdout.write(f'   📧 Enviando email: {config.email_enabled}')
            self.stdout.write(f'   📅 Creando evento calendar: {create_calendar}')

            # Enviar recordatorio
            result = gmail_service.send_reminder_email_with_calendar(
                reminder=reminder,
                create_calendar_event=create_calendar
            )

            if result['success']:
                reminder.mark_as_sent()
                self.stdout.write('   ✅ Recordatorio enviado exitosamente')
                self.stdout.write(f'   📧 ID del email: {result.get("email_id", "N/A")}')
                if result.get('calendar_event_id'):
                    self.stdout.write(f'   📅 ID del evento: {result.get("calendar_event_id")}')
                return True
            else:
                self.stdout.write(f'   ❌ Error al enviar: {result.get("error")}')
                return False

        except Exception as e:
            self.stdout.write(f'   ❌ Error inesperado: {str(e)}')
            return False

    def test_user_responses(self, reminder):
        self.stdout.write('\n👤 4. Probando respuestas de usuario...')
        
        # Simular respuesta de completado
        self.stdout.write('   🔄 Simulando respuesta "completado"...')
        reminder.mark_as_responded('completed')
        self.stdout.write('   ✅ Recordatorio marcado como completado')
        
        # Verificar que se resetee el contador de ignorados
        config = reminder.user.reminder_config
        self.stdout.write(f'   📊 Contador de ignorados: {config.consecutive_ignored}')
        
        # Crear otro recordatorio para probar ignorado
        reminder2 = Reminder.objects.create(
            user=reminder.user,
            title='🧪 Prueba de Ignorado',
            description='Recordatorio para probar función de ignorado',
            target_datetime=timezone_now() + timedelta(hours=1),
            timing='immediate'
        )
        
        self.stdout.write('   🔄 Simulando recordatorio ignorado...')
        reminder2.mark_as_ignored()
        
        # Recargar configuración
        config.refresh_from_db()
        self.stdout.write(f'   📊 Contador de ignorados actualizado: {config.consecutive_ignored}')
        
        # Limpiar recordatorio de prueba
        reminder2.delete()

    def test_cleanup_system(self):
        self.stdout.write('\n🧹 5. Probando sistema de limpieza...')
        
        # Crear recordatorio "vencido" para probar limpieza
        old_reminder = Reminder.objects.create(
            user=User.objects.first(),
            title='🧪 Recordatorio Vencido',
            description='Para probar limpieza automática',
            target_datetime=timezone_now() - timedelta(hours=2),  # Vencido
            status='pending'
        )
        
        self.stdout.write('   📝 Recordatorio vencido creado para prueba')
        
        # Simular limpieza (marcar como fallido)
        if old_reminder.target_datetime < timezone_now() - timedelta(hours=1):
            old_reminder.status = 'failed'
            old_reminder.last_error = 'Recordatorio vencido - marcado por sistema de limpieza'
            old_reminder.save()
            self.stdout.write('   ✅ Recordatorio vencido marcado como fallido')
        
        # Limpiar recordatorio de prueba
        old_reminder.delete()
        self.stdout.write('   🗑️ Recordatorio de prueba eliminado')

    def show_final_stats(self, user):
        self.stdout.write('\n📊 6. Estadísticas finales...')
        
        # Estadísticas de recordatorios
        total = user.reminders.count()
        pending = user.reminders.filter(status='pending').count()
        sent = user.reminders.filter(status='sent').count()
        completed = user.reminders.filter(status='completed').count()
        
        self.stdout.write(f'   📋 Total recordatorios: {total}')
        self.stdout.write(f'   ⏳ Pendientes: {pending}')
        self.stdout.write(f'   📤 Enviados: {sent}')
        self.stdout.write(f'   ✅ Completados: {completed}')
        
        # Estadísticas de logs
        total_logs = ReminderLog.objects.filter(reminder__user=user).count()
        recent_logs = ReminderLog.objects.filter(
            reminder__user=user,
            timestamp__gte=timezone_now() - timedelta(hours=1)
        ).count()
        
        self.stdout.write(f'   📝 Total logs: {total_logs}')
        self.stdout.write(f'   🕐 Logs última hora: {recent_logs}')
        
        # Configuración actual
        config = user.reminder_config
        self.stdout.write(f'   ⚙️ Configuración activa: {config.reminders_enabled}')
        self.stdout.write(f'   📊 Frecuencia: {getattr(config, "current_frequency", "Desconocido")}')

    def cleanup_test_data(self, user):
        """Opcional: limpiar datos de prueba"""
        test_reminders = user.reminders.filter(title__contains='🧪')
        count = test_reminders.count()
        if count > 0:
            test_reminders.delete()
            self.stdout.write(f'   🗑️ Eliminados {count} recordatorios de prueba')
