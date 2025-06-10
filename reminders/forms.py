# reminders/forms.py
from django import forms
from .models import Reminder, ReminderConfiguration, ReminderType, ReminderTiming

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = [
            'title', 'description', 'target_datetime', 
            'reminder_type', 'timing', 'ai_subject', 'ai_description'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Estudiar para examen de matemáticas'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción opcional del recordatorio...'
            }),
            'target_datetime': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'reminder_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'timing': forms.Select(attrs={
                'class': 'form-select'
            }),
            'ai_subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Asunto personalizado (opcional - la IA puede generar uno)'
            }),
            'ai_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descripción personalizada (opcional - la IA puede generar una)'
            }),
        }
        labels = {
            'title': 'Título del Recordatorio',
            'description': 'Descripción',
            'target_datetime': 'Fecha y Hora Objetivo',
            'reminder_type': 'Tipo de Recordatorio',
            'timing': 'Cuándo Recordar',
            'ai_subject': 'Asunto Personalizado (Opcional)',
            'ai_description': 'Descripción Personalizada (Opcional)',
        }

class ReminderConfigurationForm(forms.ModelForm):
    class Meta:
        model = ReminderConfiguration
        fields = [
            'reminders_enabled', 'preferred_type', 'default_timing',
            'adaptive_frequency', 'email_enabled', 'calendar_enabled'
        ]
        widgets = {
            'reminders_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'preferred_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'default_timing': forms.Select(attrs={
                'class': 'form-select'
            }),
            'adaptive_frequency': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'email_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'calendar_enabled': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'reminders_enabled': 'Activar Recordatorios',
            'preferred_type': 'Tipo Preferido',
            'default_timing': 'Tiempo de Anticipación por Defecto',
            'adaptive_frequency': 'Frecuencia Adaptativa',
            'email_enabled': 'Recordatorios por Email',
            'calendar_enabled': 'Recordatorios en Google Calendar',
        }
        help_texts = {
            'adaptive_frequency': 'El sistema ajustará automáticamente la frecuencia según tu respuesta',
            'email_enabled': 'Recibir recordatorios por correo electrónico',
            'calendar_enabled': 'Crear eventos automáticamente en Google Calendar',
        }