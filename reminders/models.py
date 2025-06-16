# reminders/models.py
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

class ReminderType(models.TextChoices):
    EMAIL = 'email', 'Solo Email'
    CALENDAR = 'calendar', 'Solo Google Calendar'
    BOTH = 'both', 'Email + Google Calendar'

class ReminderTiming(models.TextChoices):
    IMMEDIATE = 'immediate', 'Inmediato'
    MIN_15 = '15_min', '15 minutos antes'
    HOUR_1 = '1_hour', '1 hora antes'
    HOUR_2 = '2_hours', '2 horas antes'
    DAY_1 = '1_day', '1 día antes'
    DAY_3 = '3_days', '3 días antes'

class ReminderStatus(models.TextChoices):
    PENDING = 'pending', 'Pendiente'
    SENT = 'sent', 'Enviado'
    COMPLETED = 'completed', 'Completado'
    CANCELLED = 'cancelled', 'Cancelado'
    FAILED = 'failed', 'Fallido'

class ReminderFrequency(models.TextChoices):
    HIGH = 'high', 'Alta (frecuencia normal)'
    MEDIUM = 'medium', 'Media (frecuencia reducida)'
    LOW = 'low', 'Baja (frecuencia mínima)'
    DISABLED = 'disabled', 'Deshabilitado'

class ReminderConfiguration(models.Model):
    """Configuración de recordatorios por usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='reminder_config')
    reminders_enabled = models.BooleanField(default=True, verbose_name="Recordatorios activos")
    preferred_type = models.CharField(
        max_length=20, 
        choices=ReminderType.choices, 
        default=ReminderType.BOTH,
        verbose_name="Tipo preferido"
    )
    default_timing = models.CharField(
        max_length=20,
        choices=ReminderTiming.choices,
        default=ReminderTiming.HOUR_1,
        verbose_name="Tiempo de anticipación"
    )
    adaptive_frequency = models.BooleanField(default=True, verbose_name="Frecuencia adaptativa")
    current_frequency = models.CharField(
        max_length=20,
        choices=ReminderFrequency.choices,
        default=ReminderFrequency.HIGH
    )
    consecutive_ignored = models.IntegerField(default=0)
    last_adaptation = models.DateTimeField(null=True, blank=True)
    
    # Preferencias específicas
    email_enabled = models.BooleanField(default=True, verbose_name="Emails activos")
    calendar_enabled = models.BooleanField(default=True, verbose_name="Google Calendar activo")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Configuración de {self.user.get_full_name() or self.user.username}"

    def should_adapt_frequency(self):
        return self.adaptive_frequency and self.consecutive_ignored >= 3

    def adapt_frequency(self):
        if self.current_frequency == ReminderFrequency.HIGH:
            self.current_frequency = ReminderFrequency.MEDIUM
        elif self.current_frequency == ReminderFrequency.MEDIUM:
            self.current_frequency = ReminderFrequency.LOW
        
        self.consecutive_ignored = 0
        self.last_adaptation = timezone.now()
        self.save()

    class Meta:
        verbose_name = "Configuración de Recordatorio"
        verbose_name_plural = "Configuraciones de Recordatorios"

class Reminder(models.Model):
    """Recordatorio individual"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    
    # Contenido principal
    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(blank=True, verbose_name="Descripción")
    target_datetime = models.DateTimeField(verbose_name="Fecha y hora objetivo")
    
    # Configuración del recordatorio
    reminder_type = models.CharField(
        max_length=20, 
        choices=ReminderType.choices,
        default=ReminderType.BOTH,
        verbose_name="Tipo de recordatorio"
    )
    timing = models.CharField(
        max_length=20, 
        choices=ReminderTiming.choices,
        default=ReminderTiming.HOUR_1,
        verbose_name="Tiempo de anticipación"
    )
    
    # Estado y seguimiento
    status = models.CharField(
        max_length=20, 
        choices=ReminderStatus.choices, 
        default=ReminderStatus.PENDING,
        verbose_name="Estado"
    )
    scheduled_send_time = models.DateTimeField(verbose_name="Programado para")
    actual_send_time = models.DateTimeField(null=True, blank=True)
    
    # Interacción del usuario
    responded = models.BooleanField(default=False)
    response_time = models.DateTimeField(null=True, blank=True)
    response_action = models.CharField(max_length=50, blank=True)
    
    # IDs de servicios externos
    email_message_id = models.CharField(max_length=255, blank=True)
    calendar_event_id = models.CharField(max_length=255, blank=True)
    
    # Metadatos
    send_attempts = models.IntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    # IA personalization
    ai_subject = models.CharField(max_length=200, blank=True, verbose_name="Asunto generado por IA")
    ai_description = models.TextField(blank=True, verbose_name="Descripción generada por IA")
    ai_priority = models.CharField(max_length=20, default='medium')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.scheduled_send_time:
            self.calculate_send_time()
        super().save(*args, **kwargs)
    
    def calculate_send_time(self):
        """Calcula cuándo enviar el recordatorio"""
        timing_map = {
            ReminderTiming.IMMEDIATE: timedelta(0),
            ReminderTiming.MIN_15: timedelta(minutes=15),
            ReminderTiming.HOUR_1: timedelta(hours=1),
            ReminderTiming.HOUR_2: timedelta(hours=2),
            ReminderTiming.DAY_1: timedelta(days=1),
            ReminderTiming.DAY_3: timedelta(days=3),
        }
        
        time_delta = timing_map.get(ReminderTiming(self.timing), timedelta(hours=1))
        self.scheduled_send_time = self.target_datetime - time_delta
    
    def mark_as_sent(self):
        self.status = ReminderStatus.SENT
        self.actual_send_time = timezone.now()
        self.save()
    
    def mark_as_responded(self, action='completed'):
        """Marcar como respondido - RESETEA el contador de ignorados"""
        self.responded = True
        self.response_time = timezone.now()
        self.response_action = action
        self.status = ReminderStatus.COMPLETED
        self.save()
        
        # RESETEAR contador de ignorados cuando el usuario responde
        config = getattr(self.user, 'reminder_config', None)
        if config:
            config.consecutive_ignored = 0
            config.save()
    
    def mark_as_ignored(self):
        """Marcar como ignorado - INCREMENTA el contador"""
        config = getattr(self.user, 'reminder_config', None)
        if config:
            config.consecutive_ignored += 1
            
            if config.should_adapt_frequency():
                config.adapt_frequency()
            else:
                config.save()
    
    def is_ready_to_send(self):
        return (
            self.status == ReminderStatus.PENDING and
            timezone.now() >= self.scheduled_send_time
        )
    
    def get_user_full_name(self):
        """Obtiene nombre completo del usuario"""
        return f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username
    
    def __str__(self):
        return f"{self.title} - {self.get_user_full_name()}"
    
    class Meta:
        verbose_name = "Recordatorio"
        verbose_name_plural = "Recordatorios"
        ordering = ['-created_at']


class ReminderLog(models.Model):
    """Log de actividades"""
    # CAMBIO: Permitir reminder=None para logs de configuración
    reminder = models.ForeignKey(
        Reminder, 
        on_delete=models.CASCADE, 
        related_name='logs',
        null=True,  # ← AGREGAR ESTO
        blank=True  # ← AGREGAR ESTO
    )
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)
    
    # AGREGAR campo de usuario para logs sin recordatorio
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    
    def __str__(self):
        status = "✅" if self.success else "❌"
        if self.reminder:
            return f"{status} {self.action} - {self.reminder.title}"
        else:
            return f"{status} {self.action} - Sistema"
    
    @classmethod
    def log_action(cls, reminder=None, action="", details="", success=True, error_message="", user=None):
        """Crear log de acción - MEJORADO"""
        # Si hay reminder, usar su usuario; si no, usar el usuario pasado
        log_user = None
        if reminder:
            log_user = reminder.user
        elif user:
            log_user = user
            
        return cls.objects.create(
            reminder=reminder,
            user=log_user,
            action=action,
            details=details,
            success=success,
            error_message=error_message
        )
    
    class Meta:
        verbose_name = "Log de Recordatorio"
        verbose_name_plural = "Logs de Recordatorios"
        ordering = ['-timestamp']