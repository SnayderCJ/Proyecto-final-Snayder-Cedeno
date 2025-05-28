# core/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import PasswordSetupToken

def send_password_setup_email(user, token):
    """Envía el email con el código de verificación"""
    
    subject = f'Código de Verificación - {getattr(settings, "SITE_NAME", "Tu App")}'
    
    # Contexto para el template
    context = {
        'user': user,
        'code': token.token,
        'expires_minutes': 15,
        'site_name': getattr(settings, 'SITE_NAME', 'Tu App'),
    }
    
    # Renderizar template HTML - RUTA CORREGIDA
    html_message = render_to_string('password_setup_code.html', context)
    
    # Versión de texto plano
    plain_message = f"""
Hola {user.first_name or user.email},

Has solicitado establecer una contraseña para tu cuenta en {getattr(settings, 'SITE_NAME', 'Tu App')}.

Tu código de verificación es: {token.token}

Este código:
- Es válido por 15 minutos
- Solo se puede usar una vez
- Es personal e intransferible

Para mayor seguridad, no compartas este código con nadie.

Si no solicitaste este código, puedes ignorar este mensaje.

Saludos,
El equipo de {getattr(settings, 'SITE_NAME', 'Tu App')}
    """.strip()
    
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error enviando email: {e}")
        return False

def cleanup_expired_tokens():
    """Limpia tokens expirados (función para usar en un cron job)"""
    from django.utils import timezone
    
    expired_tokens = PasswordSetupToken.objects.filter(
        expires_at__lt=timezone.now(),
        is_used=False
    )
    
    count = expired_tokens.count()
    expired_tokens.delete()
    
    return count