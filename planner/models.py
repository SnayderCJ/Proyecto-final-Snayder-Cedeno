from django.db import models
from django.conf import settings  # Para importar la configuración de AUTH_USER_MODEL
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.models import User

class Event(models.Model):
    """
    Modelo para representar un evento, tarea, clase o descanso en el horario del usuario.
    """

    EVENT_TYPE_CHOICES = [
        ("tarea", "Tarea/Estudio"),
        ("clase", "Clase/Académico"),
        ("descanso", "Descanso"),
        ("personal", "Personal"),
        ("otro", "Otro"),
    ]

    PRIORITY_CHOICES = [
        ("alta", "Alta"),
        ("media", "Media"),
        ("baja", "Baja"),
    ]

    CATEGORY_CHOICES = [
        ('Matemáticas', 'Matemáticas'),
        ('Química', 'Química'),
        ('Historia', 'Historia'),
        ('Programación', 'Programación'),
        ('General', 'General'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="Usuario",
    )
    title = models.CharField(max_length=200, verbose_name="Título del Evento")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default="tarea",
        verbose_name="Tipo de Evento",
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default="media",
        verbose_name="Prioridad",
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='General',
        verbose_name="Categoría"
    )
    start_time = models.DateTimeField(verbose_name="Hora de Inicio")
    end_time = models.DateTimeField(verbose_name="Hora de Fin")
    due_date = models.DateField(
        blank=True, null=True, verbose_name="Fecha de Vencimiento"
    )
    is_completed = models.BooleanField(default=False, verbose_name="Completado")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de Creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Última Actualización"
    )

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = [
            "start_time",
            "priority",
        ]  # Ordenar eventos por hora de inicio y luego prioridad

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def clean(self):
        errors = {}
        # Validar que ambos campos de tiempo existan antes de compararlos
        if self.start_time and self.end_time:
            # Validar que la hora de fin sea posterior a la de inicio
            if self.end_time <= self.start_time:
                errors["end_time"] = (
                    "La hora de fin debe ser posterior a la hora de inicio."
                )

            # Validar duración razonable
            duration = self.end_time - self.start_time
            if duration > timedelta(hours=24):
                errors["end_time"] = "Un evento no puede durar más de 24 horas."

            if duration < timedelta(minutes=1):
                errors["end_time"] = "Un evento debe durar al menos 1 minuto."

        # Validar título
        if self.title:
            if len(self.title.strip()) < 2:
                errors["title"] = "El título debe tener al menos 2 caracteres."
        else:
            errors["title"] = "El título es obligatorio."

        # Validar fecha de vencimiento
        if self.due_date and self.start_time:
            if self.due_date < self.start_time.date():
                errors["due_date"] = (
                    "La fecha de vencimiento no puede ser anterior al inicio del evento."
                )

        # Validar combinaciones específicas
        if self.event_type == "descanso" and self.priority == "alta":
            errors["priority"] = "Los descansos no suelen necesitar prioridad alta."

        # Lanzar todas las validaciones juntas
        if errors:
            raise ValidationError(errors)
        
class BloqueEstudio(models.Model):
    TIPO_CHOICES = [
        ('estudio', 'Estudio'),
        ('descanso', 'Descanso'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='estudio')
    fecha = models.DateField(auto_now_add=True)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    duracion_min = models.IntegerField()
    completado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.usuario.username} | {self.tipo} | {self.fecha} | {self.hora_inicio}-{self.hora_fin}"
