# core/forms.py
from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from .models import PasswordSetupToken
import re

User = get_user_model()

class SettingsForm(forms.Form):
    language = forms.ChoiceField(
        label="Idiomas (Más próximamente)",
        choices=[
            ('es', 'Español'),
        ],
        widget=forms.Select(attrs={'class': 'input-field'})
    )
    timezone = forms.ChoiceField(
        label="Zona Horaria",
        choices=[
            ('America/Guayaquil', 'Ecuador (GMT-5)'),
            ('America/Lima', 'Perú (GMT-5)'),
            ('America/Bogota', 'Colombia (GMT-5)'),
            ('America/Caracas', 'Venezuela (GMT-4)'),
            ('America/La_Paz', 'Bolivia (GMT-4)'),
            ('America/Santiago', 'Chile (GMT-3/GMT-4)'),
            ('America/Argentina/Buenos_Aires', 'Argentina (GMT-3)'),
            ('America/Sao_Paulo', 'Brasil - São Paulo (GMT-3)'),
            ('America/Mexico_City', 'México Central (GMT-6)'),
            ('America/Cancun', 'México - Cancún (GMT-5)'),
            ('America/Tijuana', 'México - Tijuana (GMT-8)'),
            ('America/Guatemala', 'Guatemala (GMT-6)'),
            ('America/Tegucigalpa', 'Honduras (GMT-6)'),
            ('America/Managua', 'Nicaragua (GMT-6)'),
            ('America/Costa_Rica', 'Costa Rica (GMT-6)'),
            ('America/Panama', 'Panamá (GMT-5)'),
            ('America/Havana', 'Cuba (GMT-5)'),
            ('America/Santo_Domingo', 'República Dominicana (GMT-4)'),
            ('America/Puerto_Rico', 'Puerto Rico (GMT-4)'),
            ('Europe/Madrid', 'España (GMT+1/GMT+2)'),
            ('Europe/London', 'Reino Unido (GMT+0/GMT+1)'),
            ('Europe/Paris', 'Francia (GMT+1/GMT+2)'),
            ('Europe/Rome', 'Italia (GMT+1/GMT+2)'),
            ('Europe/Berlin', 'Alemania (GMT+1/GMT+2)'),
            ('US/Eastern', 'EE.UU. - Este (GMT-5/GMT-4)'),
            ('US/Central', 'EE.UU. - Central (GMT-6/GMT-5)'),
            ('US/Mountain', 'EE.UU. - Montaña (GMT-7/GMT-6)'),
            ('US/Pacific', 'EE.UU. - Pacífico (GMT-8/GMT-7)'),
        ],
        widget=forms.Select(attrs={'class': 'input-field', 'id': 'timezone-select'})
    )
    email_notifications = forms.BooleanField(
        label="Notificaciones por Email",
        required=False,
        help_text="Recordatorios y alertas del sistema"
    )
    task_reminders = forms.BooleanField(
        label="Recordatorio de Tareas",
        required=False,
        help_text="Alertas de vencimientos"
    )

class ProfileForm(forms.ModelForm):
    """Formulario para editar información personal"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'input-field',
                'placeholder': 'Tu nombre'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input-field', 
                'placeholder': 'Tu apellido'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input-field',
                'placeholder': 'tu_correo@ejemplo.com'
            }),
        }
        labels = {
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo Electrónico',
        }

    def __init__(self, *args, **kwargs):
        self.is_google_user = kwargs.pop('is_google_user', False)
        super().__init__(*args, **kwargs)
        
        # Si es usuario de Google, marcar campos como de solo lectura
        if self.is_google_user:
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True
            self.fields['email'].widget.attrs['readonly'] = True
            
            # Agregar clases CSS adicionales para indicar que está deshabilitado
            for field_name in ['first_name', 'last_name', 'email']:
                current_class = self.fields[field_name].widget.attrs.get('class', '')
                self.fields[field_name].widget.attrs['class'] = f"{current_class} disabled-field"

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        # Si es usuario de Google, no validar cambios (no debería poder cambiarlos)
        if self.is_google_user:
            return self.instance.email
            
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        
        # Verificar formato básico con regex más robusto
        email_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?@[a-zA-Z0-9]([a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValidationError("Ingresa una dirección de correo electrónico válida.")
        
        # Verificar longitud
        if len(email) > 254:  # RFC 5321 estándar
            raise ValidationError("El correo electrónico es demasiado largo.")
        
        # Verificar que la parte local no sea muy larga
        local_part = email.split('@')[0]
        if len(local_part) > 64:  # RFC 5321 estándar
            raise ValidationError("La parte local del correo electrónico es demasiado larga.")
        
        # Verificar que no exista ya (excluyendo el usuario actual)
        existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
        if existing_user:
            raise ValidationError("Ya existe una cuenta con este correo electrónico.")
        
        # Verificar dominios bloqueados o sospechosos (opcional)
        blocked_domains = [
            '10minutemail.com', 'temp-mail.org', 'guerrillamail.com',
            'mailinator.com', 'throwaway.email', 'tempmail.edu.vn'
        ]
        domain = email.split('@')[1].lower()
        if domain in blocked_domains:
            raise ValidationError("Este dominio de correo no está permitido.")
        
        return email

    def clean_first_name(self):
        """Validar el nombre"""
        # Si es usuario de Google, no validar cambios
        if self.is_google_user:
            return self.instance.first_name
            
        first_name = self.cleaned_data.get('first_name', '').strip()
        
        if not first_name:
            raise ValidationError("El nombre es obligatorio.")
        
        # Verificar longitud mínima y máxima
        if len(first_name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        
        if len(first_name) > 50:
            raise ValidationError("El nombre no debe exceder 50 caracteres.")
        
        # Verificar que solo contenga letras, espacios y algunos caracteres especiales
        name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\'\.]+$'
        if not re.match(name_pattern, first_name):
            raise ValidationError("El nombre solo puede contener letras, espacios, guiones y apostrofes.")
        
        # Verificar que no tenga solo espacios o caracteres especiales
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', first_name):
            raise ValidationError("El nombre debe contener al menos una letra.")
        
        # Verificar que no tenga múltiples espacios consecutivos
        if '  ' in first_name:
            raise ValidationError("El nombre no puede tener espacios consecutivos.")
        
        return first_name.title()

    def clean_last_name(self):
        """Validar el apellido"""
        # Si es usuario de Google, no validar cambios
        if self.is_google_user:
            return self.instance.last_name
            
        last_name = self.cleaned_data.get('last_name', '').strip()
        
        if not last_name:
            raise ValidationError("El apellido es obligatorio.")
        
        # Verificar longitud mínima y máxima
        if len(last_name) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        
        if len(last_name) > 50:
            raise ValidationError("El apellido no debe exceder 50 caracteres.")
        
        # Verificar que solo contenga letras, espacios y algunos caracteres especiales
        name_pattern = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s\-\'\.]+$'
        if not re.match(name_pattern, last_name):
            raise ValidationError("El apellido solo puede contener letras, espacios, guiones y apostrofes.")
        
        # Verificar que no tenga solo espacios o caracteres especiales
        if not re.search(r'[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ]', last_name):
            raise ValidationError("El apellido debe contener al menos una letra.")
        
        # Verificar que no tenga múltiples espacios consecutivos
        if '  ' in last_name:
            raise ValidationError("El apellido no puede tener espacios consecutivos.")
        
        return last_name.title()

    def clean(self):
        """Validación general del formulario"""
        cleaned_data = super().clean()
        
        # Si es usuario de Google, no permitir cambios
        if self.is_google_user:
            # Restaurar valores originales para usuarios de Google
            cleaned_data['first_name'] = self.instance.first_name
            cleaned_data['last_name'] = self.instance.last_name
            cleaned_data['email'] = self.instance.email
        
        return cleaned_data

class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulario personalizado para cambio de contraseña"""
    
    old_password = forms.CharField(
        label="Contraseña Actual",
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': '••••••••',
        }),
    )
    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': '••••••••',
        }),
        help_text="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números.",
    )
    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': '••••••••',
        }),
    )

    def clean_new_password1(self):
        """Validar la nueva contraseña"""
        password1 = self.cleaned_data.get('new_password1')
        
        if not password1:
            raise ValidationError("La nueva contraseña es obligatoria.")
        
        # Longitud mínima y máxima
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if len(password1) > 128:
            raise ValidationError("La contraseña no debe exceder 128 caracteres.")
        
        # Al menos una mayúscula
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Al menos una minúscula
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Al menos un número
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        # Opcional: al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>).")
        
        # No puede ser muy común
        common_passwords = [
            '12345678', 'password', 'contraseña', 'qwerty123', '87654321',
            'password123', 'admin123', '123456789', 'Password1', 'Qwerty123'
        ]
        if password1.lower() in [p.lower() for p in common_passwords]:
            raise ValidationError("Esta contraseña es muy común. Por favor elige una más segura.")
        
        # No puede ser igual a la contraseña actual
        old_password = self.cleaned_data.get('old_password')
        if old_password and password1 == old_password:
            raise ValidationError("La nueva contraseña debe ser diferente a la actual.")
        
        return password1

    def clean_new_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las nuevas contraseñas no coinciden.")
        
        return password2

class RequestPasswordSetupForm(forms.Form):
    """Formulario para solicitar código de verificación"""
    pass  # No necesita campos, solo confirmación

class VerifyCodeForm(forms.Form):
    """Formulario para verificar código de 6 dígitos"""
    
    code = forms.CharField(
        label="Código de Verificación",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'input-field code-input',
            'placeholder': '000000',
            'maxlength': '6',
            'pattern': '[0-9]{6}',
            'inputmode': 'numeric',
            'autocomplete': 'one-time-code',
        }),
        help_text="Ingresa el código de 6 dígitos que enviamos a tu correo"
    )
    
    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_code(self):
        """Validar el código"""
        code = self.cleaned_data.get('code', '').strip()
        
        if not code:
            raise ValidationError("El código es obligatorio.")
        
        if not re.match(r'^\d{6}$', code):
            raise ValidationError("El código debe tener exactamente 6 dígitos.")
        
        # Verificar que el código exista y sea válido
        if self.user:
            token = PasswordSetupToken.objects.filter(
                user=self.user,
                token=code,
                token_type='set_password'
            ).first()
            
            if not token:
                raise ValidationError("El código ingresado no es válido.")
            
            if not token.is_valid():
                raise ValidationError("El código ha expirado o ya fue usado. Solicita uno nuevo.")
        
        return code

class SetPasswordForm(forms.Form):
    """Formulario para establecer nueva contraseña (para usuarios de Google)"""
    
    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': '••••••••',
        }),
        help_text="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas, números y caracteres especiales.",
    )
    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'input-field',
            'placeholder': '••••••••',
        }),
    )
    
    def clean_new_password1(self):
        """Validar la nueva contraseña"""
        password1 = self.cleaned_data.get('new_password1')
        
        if not password1:
            raise ValidationError("La nueva contraseña es obligatoria.")
        
        # Longitud mínima y máxima
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        if len(password1) > 128:
            raise ValidationError("La contraseña no debe exceder 128 caracteres.")
        
        # Al menos una mayúscula
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Al menos una minúscula
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Al menos un número
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        # Al menos un carácter especial
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password1):
            raise ValidationError("La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>).")
        
        # No puede ser muy común
        common_passwords = [
            '12345678', 'password', 'contraseña', 'qwerty123', '87654321',
            'password123', 'admin123', '123456789', 'Password1', 'Qwerty123'
        ]
        if password1.lower() in [p.lower() for p in common_passwords]:
            raise ValidationError("Esta contraseña es muy común. Por favor elige una más segura.")
        
        return password1
    
    def clean_new_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las nuevas contraseñas no coinciden.")
        
        return password2