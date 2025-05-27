from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomAuthenticationForm, CustomUserCreationForm
from allauth.socialaccount.models import SocialApp
from django.utils.html import format_html

import unicodedata

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

def process_full_name(full_name):
    """Procesa el nombre completo y lo divide en first_name y last_name"""
    if not full_name:
        return "", ""
    
    names = full_name.strip().split()
    if len(names) == 1:
        return names[0].title(), ""
    elif len(names) == 2:
        return names[0].title(), names[1].title()
    elif len(names) >= 3:
        # Si hay 3 o más nombres, asumimos que los primeros son nombres y los últimos apellidos
        middle_point = len(names) // 2
        first_names = " ".join(names[:middle_point])
        last_names = " ".join(names[middle_point:])
        return first_names.title(), last_names.title()
    
    return "", ""

def login_view(request):
    if request.user.is_authenticated:
        return redirect("core:home")

    form = CustomAuthenticationForm(request, data=request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            user = form.get_user()
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
                login(request, user)
                
                # Formatear el nombre para el mensaje
                display_name = format_user_name(user)
                messages.success(request, format_html("¡Tu cuenta ha sido creada con éxito! Bienvenido, <strong>{}</strong>!", display_name))
                return redirect("core:home")
            except Exception as e:
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

def social_login_cancelled(request):
    """Vista personalizada para cuando se cancela el login social"""
    messages.info(request, "Has cancelado el inicio de sesión con Google.")
    return render(request, "login_cancelled.html")  # Quitar "accounts/"

def signout(request):
    logout(request)
    messages.info(request, "Has cerrado sesión correctamente.")
    return redirect("accounts:login")