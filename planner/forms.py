from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Event
import re

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
                'style': 'resize: vertical;',
                'maxlength': 1000
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
                'required': True,
                'style': 'min-width: 250px;'
            }, format='%Y-%m-%dT%H:%M'),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control',
                'required': True,
                'style': 'min-width: 250px;'
            }, format='%Y-%m-%dT%H:%M'),
            'due_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'placeholder': 'Fecha límite (opcional)',
                'style': 'min-width: 250px;'
            }, format='%Y-%m-%d'),
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
        self.user = kwargs.pop('user', None)  # Para validaciones específicas del usuario
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

        # Agregar help text útil
        self.fields['title'].help_text = "Nombre claro y descriptivo del evento"
        self.fields['description'].help_text = "Detalles adicionales, materiales necesarios, etc."
        self.fields['due_date'].help_text = "Solo para tareas con fecha límite específica"
        
        # Configurar valores iniciales para campos de fecha/hora al editar
        if self.instance and self.instance.pk:
            # Convertir start_time al formato datetime-local
            if self.instance.start_time:
                local_start = timezone.localtime(self.instance.start_time)
                self.fields['start_time'].widget.attrs['value'] = local_start.strftime('%Y-%m-%dT%H:%M')
                
            # Convertir end_time al formato datetime-local
            if self.instance.end_time:
                local_end = timezone.localtime(self.instance.end_time)
                self.fields['end_time'].widget.attrs['value'] = local_end.strftime('%Y-%m-%dT%H:%M')
                
            # Convertir due_date al formato date
            if self.instance.due_date:
                self.fields['due_date'].widget.attrs['value'] = self.instance.due_date.strftime('%Y-%m-%d')

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title:
            title = title.strip()
            
            # Validaciones básicas
            if len(title) < 3:
                raise ValidationError("El título debe tener al menos 3 caracteres.")
            if len(title) > 200:
                raise ValidationError("El título no puede tener más de 200 caracteres.")
            
            # Validar caracteres especiales excesivos
            if re.search(r'[!@#$%^&*()]{3,}', title):
                raise ValidationError("El título contiene demasiados caracteres especiales.")
            
            # Validar que no sea solo números o caracteres especiales
            if re.match(r'^[0-9!@#$%^&*()_\-+=\[\]{};:\'",.<>?/\\|`~]*$', title):
                raise ValidationError("El título debe contener al menos algunas letras.")
            
            # Validar palabras prohibidas o spam
            spam_patterns = ['test', 'asdf', 'qwerty', '1234']
            if any(pattern in title.lower() for pattern in spam_patterns):
                if len(title) <= 10:  # Solo para títulos cortos
                    raise ValidationError("Por favor, usa un título más descriptivo.")
            
        return title

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if description:
            description = description.strip()
            
            # Validar longitud
            if len(description) > 1000:
                raise ValidationError("La descripción no puede tener más de 1000 caracteres.")
            
            # Validar que no sea solo espacios o caracteres especiales
            if re.match(r'^[\s!@#$%^&*()_\-+=\[\]{};:\'",.<>?/\\|`~]*$', description):
                raise ValidationError("La descripción debe contener texto significativo.")
                
        return description

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if start_time:
            # Asegurarse de que start_time sea 'aware'
            if timezone.is_naive(start_time):
                local_tz = timezone.get_current_timezone()
                start_time = timezone.make_aware(start_time, timezone=local_tz)

            now_aware = timezone.now()
            
            # Validaciones temporales
            if start_time < now_aware - timedelta(days=1):
                raise ValidationError("No puedes crear eventos de hace más de un día.")
            
            if start_time > now_aware + timedelta(days=365):
                raise ValidationError("No puedes crear eventos con más de un año de anticipación.")
            
            # Validar horarios extremos
            hour = start_time.hour
            if hour < 4:
                raise ValidationError("¿Estás seguro? Programar eventos entre las 12:00 AM y 4:00 AM no es recomendable.")
            
            # Validar días de la semana para ciertos tipos
            weekday = start_time.weekday()
            if weekday == 6 and hour < 8 and self.cleaned_data.get('event_type') == 'clase':
                raise ValidationError("Los eventos académicos muy temprano en domingo pueden no ser productivos.")
        
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')
        
        if end_time and start_time:
            # Asegurarse de que end_time sea 'aware'
            if timezone.is_naive(end_time):
                local_tz = timezone.get_current_timezone()
                end_time = timezone.make_aware(end_time, timezone=local_tz)

            # Validaciones básicas de tiempo
            if end_time <= start_time:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")
            
            duration = end_time - start_time
            
            # Validaciones de duración
            if duration > timedelta(hours=12):
                raise ValidationError("Un evento no puede durar más de 12 horas.")
            
            if duration < timedelta(minutes=15):
                raise ValidationError("Un evento debe durar al menos 15 minutos.")
                
            # Validación de eventos muy largos sin descanso
            if duration > timedelta(hours=4):
                event_type = self.cleaned_data.get('event_type')
                if event_type not in ['descanso', 'personal']:
                    raise ValidationError("Eventos de estudio/trabajo de más de 4 horas deberían dividirse con descansos.")
            
            # Validar que no termine muy tarde
            if end_time.hour >= 23 or (end_time.hour == 0 and end_time.minute > 0):
                raise ValidationError("Evita programar eventos que terminen después de las 11:00 PM.")
        
        return end_time

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        start_time = self.cleaned_data.get('start_time')
        event_type = self.cleaned_data.get('event_type')
        
        if due_date:
            today_date = timezone.localdate()
            
            # Validaciones básicas
            if due_date < today_date:
                raise ValidationError("La fecha de vencimiento no puede ser en el pasado.")
            
            # Validar coherencia con start_time
            if start_time and due_date < start_time.date():
                raise ValidationError("La fecha de vencimiento no puede ser anterior al inicio del evento.")
            
            # Validar fechas muy lejanas
            if due_date > today_date + timedelta(days=365):
                raise ValidationError("La fecha de vencimiento no puede ser más de un año en el futuro.")
            
            # Validaciones específicas por tipo
            if event_type == 'clase':
                if start_time and due_date != start_time.date():
                    raise ValidationError("Para clases, la fecha de vencimiento debería ser el mismo día.")
            
            if event_type == 'descanso':
                raise ValidationError("Los descansos no necesitan fecha de vencimiento.")
        
        return due_date

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        event_type = cleaned_data.get('event_type')
        priority = cleaned_data.get('priority')
        title = cleaned_data.get('title')
        
        # Validaciones cruzadas mejoradas
        if start_time and end_time:
            start_hour = start_time.hour
            end_hour = end_time.hour
            duration = end_time - start_time
            
            # Validaciones específicas por tipo de evento
            if event_type == 'descanso':
                if duration > timedelta(hours=4):
                    self.add_error('end_time', "Los descansos no deberían durar más de 4 horas.")
                if priority == 'alta':
                    self.add_error('priority', "Los descansos raramente necesitan prioridad alta.")
            
            elif event_type == 'clase':
                if duration > timedelta(hours=6):
                    self.add_error('end_time', "Las clases no deberían durar más de 6 horas.")
                elif duration < timedelta(minutes=30):
                    self.add_error('end_time', "Las clases deberían durar al menos 30 minutos.")
                
                # Validar horarios típicos de clase
                if start_hour < 7 or start_hour > 22:
                    self.add_error('start_time', "Horarios de clase poco comunes. ¿Es correcto?")
            
            elif event_type == 'tarea':
                if duration < timedelta(minutes=30):
                    self.add_error('end_time', "Las tareas de estudio deberían durar al menos 30 minutos.")
                
                # Sugerir prioridad para tareas urgentes
                if start_time.date() == timezone.localdate() and priority == 'baja':
                    self.add_error('priority', "Tareas para hoy podrían necesitar mayor prioridad.")
            
            elif event_type == 'personal':
                if duration > timedelta(hours=8):
                    self.add_error('end_time', "Eventos personales muy largos. ¿Dividir en múltiples eventos?")
        
        # Validar conflictos de horarios si tenemos usuario
        if self.user and start_time and end_time:
            self._validate_schedule_conflicts(start_time, end_time)
        
        # Validar coherencia título-tipo
        if title and event_type:
            self._validate_title_type_consistency(title, event_type)
        
        # Validar carga de trabajo diaria
        if start_time and event_type in ['tarea', 'clase']:
            self._validate_daily_workload(start_time)
        
        return cleaned_data
    
    def _validate_schedule_conflicts(self, start_time, end_time):
        """Validar conflictos de horarios con otros eventos del usuario"""
        if not self.user:
            return
            
        # Buscar eventos superpuestos
        conflicting_events = Event.objects.filter(
            user=self.user,
            start_time__lt=end_time,
            end_time__gt=start_time
        )
        
        # Excluir el evento actual si estamos editando
        if self.instance and self.instance.pk:
            conflicting_events = conflicting_events.exclude(pk=self.instance.pk)
        
        if conflicting_events.exists():
            conflict_titles = [event.title for event in conflicting_events[:3]]
            error_msg = f"Conflicto de horario con: {', '.join(conflict_titles)}"
            if conflicting_events.count() > 3:
                error_msg += f" y {conflicting_events.count() - 3} más"
            self.add_error('start_time', error_msg)
    
    def _validate_title_type_consistency(self, title, event_type):
        """Validar que el título sea coherente con el tipo de evento"""
        title_lower = title.lower()
        
        # Palabras clave por tipo
        type_keywords = {
            'tarea': ['tarea', 'estudiar', 'examen', 'homework', 'deberes', 'revisar'],
            'clase': ['clase', 'curso', 'lectura', 'seminario', 'conferencia'],
            'descanso': ['descanso', 'break', 'pausa', 'relajar', 'dormir'],
            'personal': ['personal', 'cita', 'médico', 'familia', 'amigos']
        }
        
        # Verificar inconsistencias obvias
        for tipo, keywords in type_keywords.items():
            if tipo != event_type and any(keyword in title_lower for keyword in keywords):
                self.add_error('event_type', 
                    f"El título sugiere que es '{tipo}', ¿es correcto el tipo seleccionado?")
                break
    
    def _validate_daily_workload(self, start_time):
        """Validar que no haya sobrecarga de trabajo en un día"""
        if not self.user:
            return
            
        day_start = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Calcular horas de trabajo/estudio del día
        day_events = Event.objects.filter(
            user=self.user,
            start_time__gte=day_start,
            start_time__lt=day_end,
            event_type__in=['tarea', 'clase']
        )
        
        # Excluir evento actual si editamos
        if self.instance and self.instance.pk:
            day_events = day_events.exclude(pk=self.instance.pk)
        
        total_work_minutes = sum([
            (event.end_time - event.start_time).total_seconds() / 60
            for event in day_events
        ])
        
        # Agregar duración del evento actual
        end_time = self.cleaned_data.get('end_time')
        if end_time:
            current_duration = (end_time - start_time).total_seconds() / 60
            total_work_minutes += current_duration
        
        # Validar sobrecarga (más de 10 horas de trabajo/estudio)
        if total_work_minutes > 600:  # 10 horas
            hours = int(total_work_minutes // 60)
            self.add_error('start_time', 
                f"¡Cuidado! Tienes {hours} horas de trabajo/estudio este día. Considera agregar descansos.")

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Limpiar y normalizar datos
        if instance.title:
            instance.title = instance.title.strip()
            # Capitalizar primera letra de cada palabra importante
            instance.title = re.sub(r'\b\w+\b', lambda m: m.group(0).capitalize() 
                                  if len(m.group(0)) > 2 else m.group(0).lower(), instance.title)
        
        if instance.description:
            instance.description = instance.description.strip()
            if not instance.description:
                instance.description = None
        
        # Auto-completar campos basados en el tipo
        if instance.event_type == 'descanso' and not instance.description:
            instance.description = "Tiempo de descanso y relajación"
        
        if commit:
            instance.save()
        
        return instance