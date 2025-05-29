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
        label="Idioma",
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
            ('America/Mexico_City', 'México (GMT-6)'),
        ],
        widget=forms.Select(attrs={'class': 'input-field'})
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

    def clean_email(self):
        """Validar que el email no esté en uso por otro usuario"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        
        # Verificar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingresa una dirección de correo electrónico válida.")
        
        # Verificar que no exista ya (excluyendo el usuario actual)
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("Ya existe una cuenta con este correo electrónico.")
        
        return email

    def clean_first_name(self):
        """Validar el nombre"""
        first_name = self.cleaned_data.get('first_name', '').strip()
        
        if not first_name:
            raise ValidationError("El nombre es obligatorio.")
        
        # Verificar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', first_name):
            raise ValidationError("El nombre solo puede contener letras, espacios, guiones y apostrofes.")
        
        # Verificar longitud
        if len(first_name) < 2:
            raise ValidationError("El nombre debe tener al menos 2 caracteres.")
        
        return first_name.title()

    def clean_last_name(self):
        """Validar el apellido"""
        last_name = self.cleaned_data.get('last_name', '').strip()
        
        if not last_name:
            raise ValidationError("El apellido es obligatorio.")
        
        # Verificar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', last_name):
            raise ValidationError("El apellido solo puede contener letras, espacios, guiones y apostrofes.")
        
        # Verificar longitud
        if len(last_name) < 2:
            raise ValidationError("El apellido debe tener al menos 2 caracteres.")
        
        return last_name.title()

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
        
        # Longitud mínima
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Al menos una mayúscula
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Al menos una minúscula
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Al menos un número
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        # No puede ser muy común
        common_passwords = ['12345678', 'password', 'contraseña', 'qwerty123', '87654321']
        if password1.lower() in common_passwords:
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
        
        # Longitud mínima
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        
        # Al menos una mayúscula
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        
        # Al menos una minúscula
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        
        # Al menos un número
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        
        # No puede ser muy común
        common_passwords = ['12345678', 'password', 'contraseña', 'qwerty123', '87654321']
        if password1.lower() in common_passwords:
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