from allauth.socialaccount.models import SocialAccount
from core.models import UserProfile
import unicodedata
from datetime import date
from planner.models import BloqueEstudio, Event

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

def get_productividad_hoy(usuario):
    """Función auxiliar para obtener el porcentaje de productividad del día actual"""
    hoy = date.today()
    
    # Obtener bloques de estudio completados hoy
    bloques = BloqueEstudio.objects.filter(
        usuario=usuario,
        fecha=hoy,
        completado=True
    )
    
    # Obtener eventos completados hoy
    eventos = Event.objects.filter(
        user=usuario,
        start_time__date=hoy,
        is_completed=True,
        event_type__in=['tarea', 'clase']
    )
    
    # Calcular minutos totales
    minutos_bloques = sum(bloque.duracion_min for bloque in bloques)
    minutos_eventos = sum(
        int((evento.end_time - evento.start_time).total_seconds() / 60)
        for evento in eventos
    )
    
    minutos_totales = minutos_bloques + minutos_eventos
    meta_diaria = 120  # 2 horas
    
    # Calcular porcentaje limitado al 100%
    porcentaje = int((minutos_totales / meta_diaria) * 100) if minutos_totales > 0 else 0
    porcentaje_final = min(100, porcentaje)
    
    return porcentaje_final

def user_context(request):
    """Context processor para agregar información del usuario a todos los templates"""
    context = {}
    
    if request.user.is_authenticated:
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        
        # Obtener productividad del día actual
        productividad_hoy = get_productividad_hoy(request.user)
        
        context.update({
            'user_display_name': format_user_name(request.user),
            'user_avatar': get_user_avatar(request.user),
            'is_google_user': bool(google_account),
            'user_has_password': request.user.has_usable_password(),
            'productividad_hoy': productividad_hoy,
        })
    
    return context
