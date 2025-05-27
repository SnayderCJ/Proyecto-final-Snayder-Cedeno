from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "tu_correo@ejemplo.com",
            "id": "id_username_login",
            "required": "required",
        })
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "••••••••",
            "id": "id_password_login",
            "required": "required",
        }),
    )


class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        label="Nombre Completo",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "Tu Nombre Completo",
            "id": "id_full_name",
            "required": "required",
        }),
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            "class": "form-input",
            "placeholder": "nombre@ejemplo.com",
            "id": "id_email",
            "required": "required",
        }),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "••••••••",
            "id": "id_password1",
            "required": "required",
        }),
        help_text="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números.",
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "••••••••",
            "id": "id_password2",
            "required": "required",
        }),
    )

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "password2")

    def clean_full_name(self):
        """Validar el nombre completo"""
        full_name = self.cleaned_data.get('full_name', '').strip()
        
        if not full_name:
            raise ValidationError("El nombre completo es obligatorio.")
        
        # Verificar que tenga al menos 2 palabras (nombre y apellido)
        names = full_name.split()
        if len(names) < 2:
            raise ValidationError("Por favor ingresa tu nombre y apellido completos.")
        
        # Verificar que solo contenga letras, espacios y algunos caracteres especiales
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', full_name):
            raise ValidationError("El nombre solo puede contener letras, espacios, guiones y apostrofes.")
        
        # Verificar longitud mínima y máxima
        if len(full_name) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        
        if len(full_name) > 150:
            raise ValidationError("El nombre no puede exceder 150 caracteres.")
        
        return full_name
    
    def clean_email(self):
        """Validar el email"""
        email = self.cleaned_data.get('email', '').lower().strip()
        
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        
        # Verificar formato básico
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingresa una dirección de correo electrónico válida.")
        
        # Verificar que no exista ya
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe una cuenta con este correo electrónico.")
        
        return email
    
    def clean_password1(self):
        """Validar la contraseña"""
        password1 = self.cleaned_data.get('password1')
        
        if not password1:
            raise ValidationError("La contraseña es obligatoria.")
        
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
    
    def clean_password2(self):
        """Validar que las contraseñas coincidan"""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")
        
        return password2
    
    def clean(self):
        """Validación adicional del formulario completo"""
        cleaned_data = super().clean()
        
        # Verificar que el email no sea parte del nombre
        full_name = cleaned_data.get('full_name', '').lower()
        email = cleaned_data.get('email', '').lower()
        
        if full_name and email:
            email_prefix = email.split('@')[0]
            if email_prefix in full_name.replace(' ', ''):
                # Esta validación es opcional, puedes comentarla si es muy restrictiva
                pass
        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower().strip()
        user.email = email
        user.username = email  # usar el email como username
        
        # Procesar el nombre completo
        full_name = self.cleaned_data["full_name"].strip()
        names = full_name.split()
        
        if len(names) >= 2:
            # Si hay 2 o más nombres, dividir en nombres y apellidos
            middle_point = len(names) // 2
            first_names = " ".join(names[:middle_point])
            last_names = " ".join(names[middle_point:])
            user.first_name = first_names.title()
            user.last_name = last_names.title()
        else:
            # Solo un nombre
            user.first_name = names[0].title()
            user.last_name = ""
        
        if commit:
            user.save()
        return user