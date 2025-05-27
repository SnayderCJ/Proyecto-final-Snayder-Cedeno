from django.dispatch import receiver
from django.contrib import messages
from django.utils.html import format_html
from allauth.socialaccount.signals import pre_social_login, social_account_added

def format_user_name(user):
    """Función para formatear el nombre del usuario"""
    if user.first_name and user.last_name:
        # Dividir nombres y apellidos
        first_names = user.first_name.strip().split()
        last_names = user.last_name.strip().split()
        
        # Tomar solo el primer nombre y primer apellido
        first_name = first_names[0].title() if first_names else ""
        first_lastname = last_names[0].title() if last_names else ""
        
        return f"{first_name} {first_lastname}".strip()
    elif user.first_name:
        # Solo tiene first_name, usar solo el primer nombre
        first_names = user.first_name.strip().split()
        return first_names[0].title() if first_names else user.email
    else:
        # No tiene nombres, usar email
        return user.email

@receiver(pre_social_login)
def handle_social_login(sender, request, sociallogin, **kwargs):
    """Maneja el login social y muestra mensajes apropiados"""
    user = sociallogin.user
    
    # Si el usuario ya existe, es un login
    if user.pk:
        display_name = format_user_name(user)
        messages.success(request, format_html("¡Bienvenido de nuevo, <strong>{}</strong>!", display_name))

@receiver(social_account_added)
def handle_social_account_added(sender, request, sociallogin, **kwargs):
    """Maneja cuando se agrega una nueva cuenta social (registro)"""
    user = sociallogin.user
    display_name = format_user_name(user)
    messages.success(request, format_html("¡Tu cuenta ha sido creada con éxito! Bienvenido, <strong>{}</strong>!", display_name))