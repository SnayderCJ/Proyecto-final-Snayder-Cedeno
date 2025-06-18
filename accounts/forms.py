from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re

User = get_user_model()

# La cadena de clases de Tailwind que reemplaza a "form-input"
TAILWIND_INPUT_CLASSES = 'w-full p-3 border border-input rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-ring focus:border-ring'
TAILWIND_CODE_INPUT_CLASSES = TAILWIND_INPUT_CLASSES + ' text-center tracking-widest'

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "nombre@ejemplo.com",
            "id": "id_username_login",
        })
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "••••••••",
            "id": "id_password_login",
        }),
    )

class CustomUserCreationForm(UserCreationForm):
    full_name = forms.CharField(
        label="Nombre Completo",
        max_length=150,
        widget=forms.TextInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "Tu Nombre Completo",
            "id": "id_full_name",
            "required": "required",
        }),
    )
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "nombre@ejemplo.com",
            "id": "id_email",
            "required": "required",
        }),
    )
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "••••••••",
            "id": "id_password1",
            "required": "required",
        }),
        help_text="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números.",
    )
    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "••••••••",
            "id": "id_password2",
            "required": "required",
        }),
    )

    class Meta:
        model = User
        fields = ("full_name", "email", "password1", "password2")

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not full_name:
            raise ValidationError("El nombre completo es obligatorio.")
        names = full_name.split()
        if len(names) < 2:
            raise ValidationError("Por favor ingresa tu nombre y apellido completos.")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', full_name):
            raise ValidationError("El nombre solo puede contener letras, espacios, guiones y apostrofes.")
        if len(full_name) < 3:
            raise ValidationError("El nombre debe tener al menos 3 caracteres.")
        if len(full_name) > 150:
            raise ValidationError("El nombre no puede exceder 150 caracteres.")
        return full_name
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingresa una dirección de correo electrónico válida.")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if not password1:
            raise ValidationError("La contraseña es obligatoria.")
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        common_passwords = ['12345678', 'password', 'contraseña', 'qwerty123', '87654321']
        if password1.lower() in common_passwords:
            raise ValidationError("Esta contraseña es muy común. Por favor elige una más segura.")
        return password1
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las contraseñas no coinciden.")
        return password2
    
    def clean(self):
        return super().clean()

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower().strip()
        user.email = email
        user.username = email
        full_name = self.cleaned_data["full_name"].strip()
        names = full_name.split()
        if len(names) >= 2:
            middle_point = len(names) // 2
            first_names = " ".join(names[:middle_point])
            last_names = " ".join(names[middle_point:])
            user.first_name = first_names.title()
            user.last_name = last_names.title()
        else:
            user.first_name = names[0].title()
            user.last_name = ""
        if commit:
            user.save()
        return user

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            "class": TAILWIND_INPUT_CLASSES,
            "placeholder": "tu_correo@ejemplo.com",
            "required": "required",
        }),
        help_text="Ingresa el correo electrónico asociado a tu cuenta"
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if not email:
            raise ValidationError("El correo electrónico es obligatorio.")
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Ingresa una dirección de correo electrónico válida.")
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No existe una cuenta asociada a este correo electrónico.")
        return email

class PasswordResetVerifyForm(forms.Form):
    code = forms.CharField(
        label="Código de Verificación",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': TAILWIND_CODE_INPUT_CLASSES,
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
        code = self.cleaned_data.get('code', '').strip()
        if not code:
            raise ValidationError("El código es obligatorio.")
        if not re.match(r'^\d{6}$', code):
            raise ValidationError("El código debe tener exactamente 6 dígitos.")
        if self.user:
            from core.models import PasswordSetupToken
            token = PasswordSetupToken.objects.filter(
                user=self.user,
                token=code,
                token_type='reset_password'
            ).first()
            if not token:
                raise ValidationError("El código ingresado no es válido.")
            if not token.is_valid():
                raise ValidationError("El código ha expirado o ya fue usado. Solicita uno nuevo.")
        return code

class PasswordResetForm(forms.Form):
    new_password1 = forms.CharField(
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES,
            'placeholder': '••••••••',
        }),
        help_text="La contraseña debe tener al menos 8 caracteres, incluir mayúsculas, minúsculas y números.",
    )
    new_password2 = forms.CharField(
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': TAILWIND_INPUT_CLASSES, 
            'placeholder': '••••••••',
        }),
    )
    
    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        if not password1:
            raise ValidationError("La nueva contraseña es obligatoria.")
        if len(password1) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r'[A-Z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r'[a-z]', password1):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")
        if not re.search(r'\d', password1):
            raise ValidationError("La contraseña debe contener al menos un número.")
        common_passwords = ['12345678', 'password', 'contraseña', 'qwerty123', '87654321']
        if password1.lower() in common_passwords:
            raise ValidationError("Esta contraseña es muy común. Por favor elige una más segura.")
        return password1
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError("Las nuevas contraseñas no coinciden.")
        return password2