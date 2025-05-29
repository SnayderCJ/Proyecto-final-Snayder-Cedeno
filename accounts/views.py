from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import (
    CustomAuthenticationForm, CustomUserCreationForm,
    PasswordResetRequestForm, PasswordResetVerifyForm, PasswordResetForm
)
from allauth.socialaccount.models import SocialApp
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

# IMPORTACIONES CENTRALIZADAS
from core.models import PasswordSetupToken
from core.utils import send_password_reset_email

import unicodedata

User = get_user_model()

def normalize_text(text):
    """Normaliza el texto para manejar correctamente caracteres especiales"""
    if not text:
        return text
    
    # Normalizar Unicode y asegurar codificación correcta
    normalized = unicodedata.normalize('NFC', str(text))
    return normalized

def safe_title_case(text):
    """Aplica title case de forma segura con caracteres especiales"""
    if not text:
        return text
    
    # Normalizar primero
    text = normalize_text(text)
    
    # Dividir en palabras y capitalizar cada una
    words = []
    for word in text.split():
        if word:
            # Capitalizar la primera letra y mantener el resto en minúscula
            capitalized = word[0].upper() + word[1:].lower()
            words.append(capitalized)
    
    return ' '.join(words)

def format_user_name(user):
    """Función para formatear el nombre del usuario"""
    if user.first_name and user.last_name:
        # Normalizar y dividir nombres y apellidos
        first_names = normalize_text(user.first_name).strip().split()
        last_names = normalize_text(user.last_name).strip().split()
        
        # Tomar solo el primer nombre y primer apellido
        first_name = safe_title_case(first_names[0]) if first_names else ""
        first_lastname = safe_title_case(last_names[0]) if last_names else ""
        
        return f"{first_name} {first_lastname}".strip()
    elif user.first_name:
        # Solo tiene first_name, usar solo el primer nombre
        first_names = normalize_text(user.first_name).strip().split()
        return safe_title_case(first_names[0]) if first_names else user.email
    else:
        # No tiene nombres, usar email
        return user.email.split('@')[0] if user.email else "Usuario"

def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = CustomAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
            
            # Implementar "Recordarme"
            remember_me = request.POST.get('remember')
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # Se cierra al cerrar navegador
            
            login(request, user)
            
            # Formatear el nombre para el mensaje
            display_name = format_user_name(user)
            messages.success(request, format_html("¡Bienvenido de nuevo, <strong>{}</strong>!", display_name))
            return redirect("core:home")
        else:
            # Errores generales
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, error)
            if not messages.get_messages(request):
                messages.error(request, "Por favor, verifica tus credenciales.")

    # Verificar si Google OAuth está configurado
    google_app_configured = SocialApp.objects.filter(provider='google').exists()
    
    context = {
        "form": form,
        "google_configured": google_app_configured
    }
    return render(request, "login.html", context)

def register_view(request):
    if request.user.is_authenticated:
        return redirect("core:home") 

    form = CustomUserCreationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                user = form.save()
                # Autenticar automáticamente después del registro
                authenticated_user = authenticate(
                    username=user.email, 
                    password=form.cleaned_data['password1']
                )
                if authenticated_user:
                    login(request, authenticated_user)
                    # Formatear el nombre para el mensaje
                    display_name = format_user_name(authenticated_user)
                    messages.success(request, format_html("¡Tu cuenta ha sido creada con éxito! Bienvenido, <strong>{}</strong>!", display_name))
                    return redirect("core:home")
                else:
                    messages.error(request, "Cuenta creada exitosamente, pero hubo un problema al iniciar sesión automáticamente.")
                    return redirect("accounts:login")
            except Exception as e:
                print(f"Error en registro: {e}")  # Para debugging
                messages.error(request, "Hubo un error al crear tu cuenta. Por favor intenta de nuevo.")
        else:
            # Mostrar errores específicos de validación
            for field, errors in form.errors.items():
                for error in errors:
                    if field == '__all__':
                        messages.error(request, error)
                    else:
                        field_label = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                        messages.error(request, f"{field_label}: {error}")

    # Verificar si Google OAuth está configurado
    google_app_configured = SocialApp.objects.filter(provider='google').exists()
    
    context = {
        "form": form,
        "google_configured": google_app_configured
    }
    return render(request, "register.html", context)

# ===== NUEVAS VISTAS PARA RECUPERACIÓN DE CONTRASEÑA =====

def password_reset_request(request):
    """Vista para solicitar recuperación de contraseña"""
    if request.user.is_authenticated:
        return redirect("core:home")
    
    form = PasswordResetRequestForm()
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            # Obtener el email del formulario y buscar el usuario
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "No existe una cuenta asociada a ese correo electrónico.")
                return render(request, 'emails/password_reset_request.html', {'form': form})

            # Invalidar tokens anteriores del usuario
            PasswordSetupToken.objects.filter(
                user=user,
                token_type='reset_password',
                is_used=False
            ).update(is_used=True)
            
            # Crear nuevo token
            token = PasswordSetupToken.objects.create(
                user=user,
                token_type='reset_password'
            )
            
            # Enviar email
            if send_password_reset_email(user, token):
                messages.success(request, format_html(
                    "¡Código enviado! Revisa tu correo <strong>{}</strong> y ingresa el código de 6 dígitos.",
                    email
                ))
                # Guardar email en sesión para el siguiente paso
                request.session['reset_email'] = email
                return redirect('accounts:password_reset_verify')
            else:
                messages.error(request, "Hubo un error enviando el código. Por favor intenta de nuevo.")
    
    context = {
        'form': form,
    }
    return render(request, 'emails/password_reset_request.html', context)

def password_reset_verify(request):
    """Vista para verificar código de recuperación"""
    if request.user.is_authenticated:
        return redirect("core:home")
    
    # Verificar que tengamos el email en sesión
    if 'reset_email' not in request.session:
        messages.error(request, "Sesión expirada. Solicita un nuevo código.")
        return redirect('accounts:password_reset_request')
    
    email = request.session['reset_email']
    user = get_object_or_404(User, email=email)
    form = PasswordResetVerifyForm(user=user)
    
    if request.method == 'POST':
        form = PasswordResetVerifyForm(user=user, data=request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Buscar y validar token
            token = PasswordSetupToken.objects.filter(
                user=user,
                token=code,
                token_type='reset_password'
            ).first()
            
            if token and token.is_valid():
                # Guardar token en sesión para el siguiente paso
                request.session['verified_reset_token_id'] = token.id
                messages.success(request, "¡Código verificado correctamente! Ahora establece tu nueva contraseña.")
                return redirect('accounts:password_reset_confirm')
            else:
                messages.error(request, "El código es inválido o ha expirado.")
    
    context = {
        'form': form,
        'user_email': email,
    }
    return render(request, 'emails/password_reset_verify.html', context)

def password_reset_confirm(request):
    """Vista para establecer nueva contraseña"""
    if request.user.is_authenticated:
        return redirect("core:home")
    
    # Verificar permisos y token en sesión
    if ('reset_email' not in request.session or 
        'verified_reset_token_id' not in request.session):
        messages.error(request, "Sesión expirada. Solicita un nuevo código.")
        return redirect('accounts:password_reset_request')
    
    # Verificar que el token siga siendo válido
    token = get_object_or_404(
        PasswordSetupToken,
        id=request.session['verified_reset_token_id'],
        token_type='reset_password'
    )
    
    if not token.is_valid():
        # Limpiar sesión
        if 'reset_email' in request.session:
            del request.session['reset_email']
        if 'verified_reset_token_id' in request.session:
            del request.session['verified_reset_token_id']
        messages.error(request, "El código ha expirado. Solicita uno nuevo.")
        return redirect('accounts:password_reset_request')
    
    form = PasswordResetForm()
    
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Establecer la nueva contraseña
            user = token.user
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            # Limpiar sesión
            if 'reset_email' in request.session:
                del request.session['reset_email']
            if 'verified_reset_token_id' in request.session:
                del request.session['verified_reset_token_id']
            
            messages.success(request, format_html(
                "¡Contraseña cambiada exitosamente! Ya puedes iniciar sesión con tu nueva contraseña."
            ))
            return redirect('accounts:login')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                    messages.error(request, f"{field_label}: {error}")
    
    context = {
        'form': form,
        'token': token,
    }
    return render(request, 'emails/password_reset_confirm.html', context)

def social_login_cancelled(request):
    """Vista personalizada para cuando se cancela el login social"""
    messages.info(request, "Has cancelado el inicio de sesión con Google.")
    return render(request, "login_cancelled.html")

@login_required
def signout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("accounts:login")