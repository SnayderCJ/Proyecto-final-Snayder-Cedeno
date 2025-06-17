from django.db import models
from django.conf import settings # Para importar la configuración de AUTH_USER_MODEL

class Event(models.Model):
    """
    Modelo para representar un evento, tarea, clase o descanso en el horario del usuario.
    """
    EVENT_TYPE_CHOICES = [
        ('tarea', 'Tarea/Estudio'),
        ('clase', 'Clase/Académico'),
        ('descanso', 'Descanso'),
        ('personal', 'Personal'),
        ('otro', 'Otro'),
    ]

    PRIORITY_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Usuario'
    )
    title = models.CharField(max_length=200, verbose_name='Título del Evento')
    description = models.TextField(blank=True, null=True, verbose_name='Descripción')
    event_type = models.CharField(
        max_length=20,
        choices=EVENT_TYPE_CHOICES,
        default='tarea',
        verbose_name='Tipo de Evento'
    )
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='media',
        verbose_name='Prioridad'
    )
    start_time = models.DateTimeField(verbose_name='Hora de Inicio')
    end_time = models.DateTimeField(verbose_name='Hora de Fin')
    due_date = models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')
    is_completed = models.BooleanField(default=False, verbose_name='Completado')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['start_time', 'priority'] # Ordenar eventos por hora de inicio y luego prioridad

    def __str__(self):
        return f"{self.title} ({self.user.username})"

    def clean(self):
        # Validación personalizada a nivel de modelo (opcional, también se hace en el formulario)
        from django.core.exceptions import ValidationError
        if self.end_time < self.start_time:
            raise ValidationError('La hora de fin no puede ser anterior a la hora de inicio.')
#------------------------------------------------
from django.db import models
from django.contrib.auth.models import User

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
