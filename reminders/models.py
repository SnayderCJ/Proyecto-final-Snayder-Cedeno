from django.db import models
from django.conf import settings
from django.utils import timezone


class ReminderConfig(models.Model):
    """Configuración de recordatorios por usuario"""

    REMINDER_TYPES = [
        ("email", "Solo Email"),
        ("calendar", "Solo Calendario"),
        ("both", "Email y Calendario"),
    ]

    FREQUENCY_CHOICES = [
        ("low", "Baja (1 recordatorio)"),
        ("normal", "Normal (2 recordatorios)"),
        ("high", "Alta (3 recordatorios)"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reminder_config",
    )

    # Configuración general
    reminders_enabled = models.BooleanField(default=True)
    email_enabled = models.BooleanField(default=True)
    calendar_enabled = models.BooleanField(default=True)

    # Preferencias
    preferred_type = models.CharField(
        max_length=10, choices=REMINDER_TYPES, default="both"
    )
    current_frequency = models.CharField(
        max_length=10, choices=FREQUENCY_CHOICES, default="normal"
    )

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Configuración de recordatorios para {self.user.email}"


class Reminder(models.Model):
    """Modelo para recordatorios"""

    STATUS_CHOICES = [
        ("pending", "Pendiente"),
        ("sent", "Enviado"),
        ("completed", "Completado"),
        ("cancelled", "Cancelado"),
        ("failed", "Fallido"),
    ]

    REMINDER_TYPES = [
        ("email", "Email"),
        ("calendar", "Calendario"),
        ("both", "Ambos"),
    ]

    TIMING_CHOICES = [
        ("immediate", "Inmediato"),
        ("5min", "5 minutos antes"),
        ("15min", "15 minutos antes"),
        ("30min", "30 minutos antes"),
        ("1hour", "1 hora antes"),
        ("1day", "1 día antes"),
    ]

    # Relaciones
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reminders"
    )

    # Datos básicos
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_datetime = models.DateTimeField()

    # Configuración
    reminder_type = models.CharField(
        max_length=10, choices=REMINDER_TYPES, default="email"
    )
    timing = models.CharField(max_length=10, choices=TIMING_CHOICES, default="15min")

    # Estado y seguimiento
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    send_attempts = models.PositiveIntegerField(default=0)
    last_attempt = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)

    # Datos de IA
    ai_subject = models.CharField(max_length=200, blank=True)
    ai_description = models.TextField(blank=True)

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_send_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        # Calcular tiempo de envío programado si es nuevo
        if not self.id:
            self.scheduled_send_time = self.calculate_send_time()
        super().save(*args, **kwargs)

    def calculate_send_time(self):
        """Calcula cuándo debe enviarse el recordatorio basado en timing"""
        if self.timing == "immediate":
            return timezone.now()

        delta = {
            "5min": timezone.timedelta(minutes=5),
            "15min": timezone.timedelta(minutes=15),
            "30min": timezone.timedelta(minutes=30),
            "1hour": timezone.timedelta(hours=1),
            "1day": timezone.timedelta(days=1),
        }.get(self.timing, timezone.timedelta(minutes=15))

        return self.target_datetime - delta

    def mark_as_sent(self):
        """Marca el recordatorio como enviado"""
        self.status = "sent"
        self.last_attempt = timezone.now()
        self.send_attempts += 1
        self.save()

    def mark_as_completed(self):
        """Marca el recordatorio como completado"""
        self.status = "completed"
        self.save()

    def mark_as_failed(self, error_message):
        """Marca el recordatorio como fallido"""
        self.status = "failed"
        self.last_error = error_message
        self.last_attempt = timezone.now()
        self.send_attempts += 1
        self.save()

    def cancel(self):
        """Cancela el recordatorio"""
        self.status = "cancelled"
        self.save()

    def snooze(self, minutes=15):
        """Pospone el recordatorio"""
        self.target_datetime = timezone.now() + timezone.timedelta(minutes=minutes)
        self.scheduled_send_time = self.calculate_send_time()
        self.status = "pending"
        self.save()

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    class Meta:
        ordering = ["scheduled_send_time"]
        indexes = [
            models.Index(fields=["status", "scheduled_send_time"]),
            models.Index(fields=["user", "status"]),
        ]


class ReminderLog(models.Model):
    """Registro de actividad de recordatorios"""

    reminder = models.ForeignKey(
        Reminder, on_delete=models.CASCADE, related_name="logs"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=50)
    details = models.TextField(blank=True)
    success = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.action} - {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]
