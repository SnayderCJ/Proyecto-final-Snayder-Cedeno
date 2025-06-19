from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import timedelta
from reminders.models import Reminder, ReminderConfiguration
from planner.models import Event

class Command(BaseCommand):
    help = 'Sincroniza eventos del planner con recordatorios automáticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username específico para sincronizar (opcional)',
        )
        parser.add_argument(
            '--days-ahead',
            type=int,
            default=7,
            help='Días hacia adelante para crear recordatorios (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo simulación sin crear recordatorios',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        days_ahead = options['days_ahead']
        username = options.get('user')
        now = timezone.now()
        future_limit = now + timedelta(days=days_ahead)

        self.stdout.write(f"🔄 Sincronizando eventos del planner con recordatorios...")
        self.stdout.write(f"📅 Rango: {now.strftime('%Y-%m-%d')} a {future_limit.strftime('%Y-%m-%d')}")

        # Filtrar usuarios
        if username:
            try:
                users = [User.objects.get(username=username)]
                self.stdout.write(f"👤 Sincronizando solo usuario: {username}")
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Usuario '{username}' no encontrado"))
                return
        else:
            users = User.objects.filter(is_active=True)
            self.stdout.write(f"👥 Sincronizando {users.count()} usuarios activos")

        total_created = 0
        total_skipped = 0

        for user in users:
            try:
                # Obtener configuración del usuario
                config, created = ReminderConfiguration.objects.get_or_create(
                    user=user,
                    defaults={'reminders_enabled': True}
                )

                if not config.reminders_enabled:
                    self.stdout.write(f"⏭️ Saltando {user.username}: recordatorios deshabilitados")
                    continue

                # Obtener eventos futuros del usuario
                events = Event.objects.filter(
                    user=user,
                    start_time__gte=now,
                    start_time__lte=future_limit,
                    is_completed=False
                )

                self.stdout.write(f"\n👤 {user.username}: {events.count()} eventos encontrados")

                for event in events:
                    # Verificar si ya existe un recordatorio para este evento
                    existing_reminder = Reminder.objects.filter(
                        user=user,
                        title__icontains=event.title,
                        target_datetime__date=event.start_time.date()
                    ).first()

                    if existing_reminder:
                        total_skipped += 1
                        continue

                    # Crear recordatorio basado en la configuración del usuario
                    reminder_data = {
                        'user': user,
                        'title': f"📚 {event.title}",
                        'description': self._generate_reminder_description(event),
                        'target_datetime': event.start_time,
                        'reminder_type': config.preferred_type,
                        'timing': config.default_timing,
                    }

                    if dry_run:
                        self.stdout.write(f"🔸 [DRY RUN] Crearía recordatorio: {reminder_data['title']}")
                        total_created += 1
                    else:
                        reminder = Reminder.objects.create(**reminder_data)
                        self.stdout.write(f"✅ Creado: {reminder.title} ({reminder.scheduled_send_time.strftime('%Y-%m-%d %H:%M')})")
                        total_created += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error procesando {user.username}: {str(e)}"))

        # Resumen
        self.stdout.write(f"\n📊 Resumen de sincronización:")
        self.stdout.write(f"✅ Recordatorios creados: {total_created}")
        self.stdout.write(f"⏭️ Eventos saltados (ya tienen recordatorio): {total_skipped}")

        if dry_run:
            self.stdout.write(f"🔸 Modo simulación - No se crearon recordatorios reales")
        else:
            self.stdout.write(self.style.SUCCESS("✅ Sincronización completada"))

    def _generate_reminder_description(self, event):
        """Genera una descripción inteligente para el recordatorio"""
        description = f"<h3>📚 {event.title}</h3>"
        
        if event.description:
            description += f"<p><strong>Descripción:</strong> {event.description}</p>"
        
        description += f"<p><strong>📅 Fecha:</strong> {event.start_time.strftime('%d/%m/%Y')}</p>"
        description += f"<p><strong>⏰ Hora:</strong> {event.start_time.strftime('%H:%M')}</p>"
        
        if hasattr(event, 'category') and event.category:
            description += f"<p><strong>📂 Categoría:</strong> {event.category}</p>"
        
        # Agregar consejos basados en el tipo de evento
        if any(word in event.title.lower() for word in ['examen', 'prueba', 'test']):
            description += """
            <div style="background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>💡 Consejos para el examen:</strong>
                <ul>
                    <li>Revisa tus apuntes una última vez</li>
                    <li>Prepara todos los materiales necesarios</li>
                    <li>Descansa bien la noche anterior</li>
                </ul>
            </div>
            """
        elif any(word in event.title.lower() for word in ['tarea', 'entrega', 'proyecto']):
            description += """
            <div style="background: #d1ecf1; padding: 10px; border-radius: 5px; margin: 10px 0;">
                <strong>📝 Recordatorio de entrega:</strong>
                <ul>
                    <li>Verifica que tengas todo completo</li>
                    <li>Revisa los requisitos de formato</li>
                    <li>Haz una copia de seguridad</li>
                </ul>
            </div>
            """
        
        return description
