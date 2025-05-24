from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # usar el email como username
        user.first_name = self.cleaned_data["full_name"]
        if commit:
            user.save()
        return user
