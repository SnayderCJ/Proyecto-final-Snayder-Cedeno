# PLANIFICADOR_IA/planner/forms.py

from django import forms
from .models import Event # Importa tu modelo Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'event_type', 'priority', 'start_time', 'end_time', 'due_date', 'is_completed']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Título del evento'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 3, 'placeholder': 'Descripción detallada'}),
            'event_type': forms.Select(attrs={'class': 'input-field'}),
            'priority': forms.Select(attrs={'class': 'input-field'}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input-field'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'input-field'}),
            'due_date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'is_completed': forms.CheckboxInput(attrs={'class': 'checkbox-field'}),
        }
        labels = {
            'title': 'Título',
            'description': 'Descripción',
            'event_type': 'Tipo de Evento',
            'priority': 'Prioridad',
            'start_time': 'Hora de Inicio',
            'end_time': 'Hora de Fin',
            'due_date': 'Fecha de Vencimiento (Opcional)',
            'is_completed': 'Completado',
        }

    # Puedes añadir lógica de validación personalizada aquí si es necesario
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        due_date = cleaned_data.get('due_date') # Para tareas que tienen due_date

        if start_time and end_time:
            if end_time < start_time:
                raise forms.ValidationError("La hora de fin no puede ser anterior a la hora de inicio.")
            # Puedes añadir más validación, como que los eventos no se superpongan para el mismo usuario

        # Lógica de validación para due_date vs event_type (opcional)
        event_type = cleaned_data.get('event_type')
        if event_type == 'tarea' and not due_date:
            # Puedes hacer que due_date sea obligatorio para tareas si lo deseas
            # self.add_error('due_date', "Las tareas deben tener una fecha de vencimiento.")
            pass # Por ahora, lo dejamos opcional

        return cleaned_data