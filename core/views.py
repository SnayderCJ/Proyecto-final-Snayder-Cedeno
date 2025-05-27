from django.shortcuts import render
from allauth.socialaccount.models import SocialAccount
from datetime import datetime
import unicodedata

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
            'google_avatar': google_account.extra_data.get('picture') if google_account else None,
        })
    
    return render(request, 'pages/home.html', context)

def perfil(request):
    google_account = None
    google_avatar = None
    is_google_user = False

    context = {
        'greeting': get_greeting(),
        'current_date': get_formatted_date(),
    }

    if request.user.is_authenticated:
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        if google_account:
            is_google_user = True
            google_avatar = google_account.extra_data.get('picture')

        context.update({
            'user_display_name': format_user_name(request.user),
            'is_google_user': is_google_user,
            'google_avatar': google_avatar,
        })

    return render(request, 'pages/perfil.html', context)