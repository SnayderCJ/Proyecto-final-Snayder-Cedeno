# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from allauth.socialaccount.models import SocialAccount
from .forms import (
    SettingsForm, ProfileForm, CustomPasswordChangeForm,
    VerifyCodeForm, SetPasswordForm
)
from .models import UserSettings, PasswordSetupToken, UserProfile
from .utils import send_password_setup_email
from datetime import datetime
import unicodedata
import json

@login_required
def home(request):
    context = {
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
    }
    
    # Agregar información del usuario y Google si está autenticado
    if request.user.is_authenticated:
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        
        context.update({
            'user_display_name': format_user_name(request.user),
            'is_google_user': bool(google_account),
            'user_avatar': get_user_avatar(request.user),
        })
    
    return render(request, 'pages/home.html', context)

def normalize_text(text):
    """Normaliza el texto para manejar correctamente caracteres especiales"""
    if not text:
        return text
    
    # Normalizar Unicode y asegurar codificación correcta
    normalized = unicodedata.normalize('NFC', str(text))
    return normalized

def get_greeting():
    """Devuelve el saludo apropiado según la hora del día"""
    now = datetime.now()
    hour = now.hour
    
    if 5 <= hour < 12:
        return "Buenos días"
    elif 12 <= hour < 19:
        return "Buenas tardes"
    else:
        return "Buenas noches"

def get_formatted_date():
    """Devuelve la fecha formateada en español"""
    now = datetime.now()
    
    # Nombres de días y meses en español
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    day_name = days[now.weekday()]
    day_number = now.day
    month_name = months[now.month - 1]
    year = now.year
    
    return f"{day_name}, {day_number} de {month_name} de {year}"

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
    """Función para formatear el nombre del usuario (primer nombre + primer apellido)"""
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

def get_user_avatar(user):
    """Función para obtener el avatar del usuario (personalizado o de Google)"""
    # Primero verificar si tiene avatar personalizado
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.avatar:
            return profile.avatar.url
    except UserProfile.DoesNotExist:
        pass
    
    # Si no tiene avatar personalizado, verificar si es usuario de Google
    google_account = SocialAccount.objects.filter(user=user, provider='google').first()
    if google_account and 'picture' in google_account.extra_data:
        return google_account.extra_data['picture']
    
    # Si no tiene ningún avatar, retornar None
    return None


@login_required
def perfil(request):
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    is_google_user = bool(google_account)
    user_has_password = request.user.has_usable_password()
    
    # Obtener o crear perfil del usuario
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Inicializar formularios
    profile_form = ProfileForm(instance=request.user)
    password_form = CustomPasswordChangeForm(request.user) if user_has_password else None
    
    # Procesamiento de formularios
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile' and not is_google_user:
            profile_form = ProfileForm(request.POST, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                # Actualizar el username con el nuevo email
                request.user.username = request.user.email
                request.user.save()
                messages.success(request, format_html("¡Tu información personal ha sido actualizada exitosamente!"))
                return redirect('core:perfil')
            else:
                # Mostrar errores específicos
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        field_label = profile_form.fields[field].label if field in profile_form.fields else field.replace('_', ' ').title()
                        messages.error(request, f"{field_label}: {error}")
        
        elif form_type == 'password' and user_has_password:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Mantener la sesión activa después del cambio de contraseña
                update_session_auth_hash(request, user)
                messages.success(request, format_html("¡Tu contraseña ha sido cambiada exitosamente!"))
                return redirect('core:perfil')
            else:
                # Mostrar errores específicos
                for field, errors in password_form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            field_label = password_form.fields[field].label if field in password_form.fields else field.replace('_', ' ').title()
                            messages.error(request, f"{field_label}: {error}")

    context = {
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
        'user_display_name': format_user_name(request.user),
        'is_google_user': is_google_user,
        'user_has_password': user_has_password,
        'user_avatar': get_user_avatar(request.user),
        'profile_form': profile_form,
        'password_form': password_form,
    }

    return render(request, 'pages/perfil.html', context)

@login_required
@require_http_methods(["POST"])
def upload_avatar(request):
    """Vista para subir foto de perfil vía AJAX"""
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            })
        
        avatar_file = request.FILES['avatar']
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de archivo no permitido. Solo se permiten JPG, PNG y GIF.'
            })
        
        # Validar tamaño (5MB máximo)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 5MB.'
            })
        
        # Obtener o crear perfil del usuario
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Actualizar avatar
        user_profile.avatar = avatar_file
        user_profile.save()
        
        return JsonResponse({
            'success': True,
            'avatar_url': user_profile.avatar.url,
            'message': '¡Foto de perfil actualizada exitosamente!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al subir la imagen: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def remove_avatar(request):
    """Vista para eliminar foto de perfil"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.avatar:
            # Eliminar archivo físico
            if user_profile.avatar.path:
                import os
                if os.path.isfile(user_profile.avatar.path):
                    os.remove(user_profile.avatar.path)
            
            # Limpiar campo de la base de datos
            user_profile.avatar = None
            user_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Foto de perfil eliminada exitosamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No tienes una foto de perfil para eliminar'
            })
            
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Perfil no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar la imagen: {str(e)}'
        })

@login_required
def request_password_setup(request):
    """Vista para solicitar código de verificación para establecer contraseña"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Solo usuarios de Google sin contraseña pueden acceder
    if not google_account or request.user.has_usable_password():
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    if request.method == 'POST':
        # Invalidar tokens anteriores del usuario
        PasswordSetupToken.objects.filter(
            user=request.user,
            token_type='set_password',
            is_used=False
        ).update(is_used=True)
        
        # Crear nuevo token
        token = PasswordSetupToken.objects.create(
            user=request.user,
            token_type='set_password'
        )
        
        # Enviar email
        if send_password_setup_email(request.user, token):
            messages.success(request, format_html(
                "¡Código enviado! Revisa tu correo <strong>{}</strong> y ingresa el código de 6 dígitos.",
                request.user.email
            ))
            return redirect('core:verify_password_code')
        else:
            messages.error(request, "Hubo un error enviando el código. Por favor intenta de nuevo.")
    
    context = {
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
        'user_display_name': format_user_name(request.user),
        'user_avatar': get_user_avatar(request.user),
    }
    
    return render(request, 'pages/emails/request_password_setup.html', context)

@login_required
def verify_password_code(request):
    """Vista para verificar código de 6 dígitos"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Solo usuarios de Google sin contraseña pueden acceder
    if not google_account or request.user.has_usable_password():
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    form = VerifyCodeForm(user=request.user)
    
    if request.method == 'POST':
        form = VerifyCodeForm(user=request.user, data=request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Buscar y validar token
            token = PasswordSetupToken.objects.filter(
                user=request.user,
                token=code,
                token_type='set_password'
            ).first()
            
            if token and token.is_valid():
                # Guardar token en sesión para el siguiente paso
                request.session['verified_token_id'] = token.id
                messages.success(request, "¡Código verificado correctamente! Ahora establece tu contraseña.")
                return redirect('core:set_password')
            else:
                messages.error(request, "El código es inválido o ha expirado.")
    
    context = {
        'form': form,
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
        'user_display_name': format_user_name(request.user),
        'user_email': request.user.email,
        'user_avatar': get_user_avatar(request.user),
    }
    
    return render(request, 'pages/emails/verify_password_code.html', context)

@login_required
def set_password(request):
    """Vista para establecer nueva contraseña después de verificar código"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Verificar permisos y token en sesión
    if (not google_account or 
        request.user.has_usable_password() or 
        'verified_token_id' not in request.session):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    # Verificar que el token siga siendo válido
    token = get_object_or_404(
        PasswordSetupToken,
        id=request.session['verified_token_id'],
        user=request.user,
        token_type='set_password'
    )
    
    if not token.is_valid():
        del request.session['verified_token_id']
        messages.error(request, "El código ha expirado. Solicita uno nuevo.")
        return redirect('core:request_password_setup')
    
    form = SetPasswordForm()
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Establecer la nueva contraseña
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            # Limpiar sesión
            del request.session['verified_token_id']
            
            # Mantener la sesión activa
            update_session_auth_hash(request, request.user)
            
            messages.success(request, format_html(
                "¡Contraseña establecida correctamente! Ahora puedes usar tanto Google como tu contraseña para iniciar sesión."
            ))
            return redirect('core:perfil')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                    messages.error(request, f"{field_label}: {error}")
    
    context = {
        'form': form,
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
        'user_display_name': format_user_name(request.user),
        'user_avatar': get_user_avatar(request.user),
        'token': token,
    }
    
    return render(request, 'pages/emails/set_password.html', context)

@login_required
def settings(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST)
        if form.is_valid():
            user_settings.language = form.cleaned_data['language']
            user_settings.timezone = form.cleaned_data['timezone']
            user_settings.save()
            messages.success(request, "¡Tus configuraciones han sido guardadas exitosamente!")
            return redirect('core:settings')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = SettingsForm(initial={
            'language': user_settings.language,
            'timezone': user_settings.timezone
        })

    context = {
        'form': form,
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
        'user_avatar': get_user_avatar(request.user),
    }

    return render(request, 'pages/settings.html', context)