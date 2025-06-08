from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'priority', 'start_time', 'end_time', 'due_date', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Ej: Estudiar para examen de matemáticas',
                'required': True,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Descripción detallada del evento (opcional)',
                'style': 'resize: vertical;'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'priority': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True
            }),
            'due_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'placeholder': 'Fecha límite (opcional)'
            }),
            'is_completed': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'title': 'Título del Evento',
            'description': 'Descripción',
            'event_type': 'Tipo de Evento',
            'priority': 'Prioridad',
            'start_time': 'Fecha y Hora de Inicio',
            'end_time': 'Fecha y Hora de Fin',
            'due_date': 'Fecha de Vencimiento',
            'is_completed': 'Marcar como Completado',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar opciones de select con emojis
        self.fields['event_type'].choices = [
            ('', 'Selecciona un tipo...'),
            ('tarea', '📚 Tarea/Estudio'),
            ('clase', '🎓 Clase/Académico'),
            ('descanso', '☕ Descanso'),
            ('personal', '👤 Personal'),
            ('otro', '📝 Otro'),
        ]
        
        self.fields['priority'].choices = [
            ('', 'Selecciona prioridad...'),
            ('alta', '🔴 Alta Prioridad'),
            ('media', '🟡 Prioridad Media'),
            ('baja', '🟢 Baja Prioridad'),
        ]

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            if len(title) < 3:
                raise ValidationError("El título debe tener al menos 3 caracteres.")
            if len(title) > 200:
                raise ValidationError("El título no puede tener más de 200 caracteres.")
        return title

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        
        if start_time:
            # Verificar que no sea muy en el pasado (más de 1 día)
            if start_time < datetime.now() - timedelta(days=1):
                raise ValidationError("No puedes crear eventos de hace más de un día.")
            
            # Verificar que no sea muy en el futuro (más de 1 año)
            if start_time > datetime.now() + timedelta(days=365):
                raise ValidationError("No puedes crear eventos con más de un año de anticipación.")
        
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')
        
        if end_time and start_time:
            if end_time <= start_time:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            
            # Verificar duración máxima (12 horas)
            duration = end_time - start_time
            if duration > timedelta(hours=12):
                raise ValidationError("Un evento no puede durar más de 12 horas.")
            
            # Verificar duración mínima (15 minutos)
            if duration < timedelta(minutes=15):
                raise ValidationError("Un evento debe durar al menos 15 minutos.")
        
        return end_time

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        start_time = self.cleaned_data.get('start_time')
        
        if due_date:
            # Verificar que la fecha de vencimiento no sea en el pasado
            if due_date < datetime.now().date():
                raise ValidationError("La fecha de vencimiento no puede ser en el pasado.")
            
            # Si hay start_time, verificar coherencia
            if start_time and due_date < start_time.date():
                raise ValidationError("La fecha de vencimiento no puede ser anterior al inicio del evento.")
        
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        event_type = cleaned_data.get('event_type')
        
        # Validaciones cruzadas adicionales
        if start_time and end_time:
            # Verificar horarios razonables
            start_hour = start_time.hour
            end_hour = end_time.hour
            
            if start_hour < 5 or start_hour > 23:
                self.add_error('start_time', "¿Estás seguro de programar un evento a esta hora? (5:00-23:00 recomendado)")
            
            if end_hour < 5 or end_hour > 23:
                self.add_error('end_time', "¿Estás seguro de programar un evento a esta hora? (5:00-23:00 recomendado)")
        
        # Validaciones específicas por tipo de evento
        if event_type and start_time and end_time:
            duration = end_time - start_time
            
            if event_type == 'descanso':
                if duration > timedelta(hours=4):
                    self.add_error('end_time', "Los descansos no deberían durar más de 4 horas.")
            
            elif event_type == 'clase':
                if duration > timedelta(hours=6):
                    self.add_error('end_time', "Las clases no deberían durar más de 6 horas.")
                elif duration < timedelta(minutes=30):
                    self.add_error('end_time', "Las clases deberían durar al menos 30 minutos.")
            
            elif event_type == 'tarea':
                if duration < timedelta(minutes=30):
                    self.add_error('end_time', "Las tareas de estudio deberían durar al menos 30 minutos.")
        
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Limpiar y normalizar el título
        if instance.title:
            instance.title = instance.title.strip()
        
        # Limpiar descripción
        if instance.description:
            instance.description = instance.description.strip()
            if not instance.description:
                instance.description = None
        
        if commit:
            instance.save()
        
        return instance