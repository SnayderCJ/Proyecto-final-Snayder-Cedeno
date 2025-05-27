from django.contrib import messages
from django.utils.html import format_html

class CleanSocialLoginMessagesMiddleware:
    """Middleware para limpiar mensajes de allauth y reemplazarlos con los nuestros"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si el usuario está autenticado, limpiar mensajes de allauth
        if request.user.is_authenticated:
            # Obtener todos los mensajes
            storage = messages.get_messages(request)
            messages_list = list(storage)
            
            # Buscar mensajes de allauth que queremos reemplazar
            has_allauth_message = False
            for message in messages_list:
                message_text = str(message.message).lower()
                # Detectar mensajes de allauth
                if any(phrase in message_text for phrase in [
                    'ha iniciado sesión exitosamente como',
                    'exitosamente como',
                    'successfully signed in as',
                    'logged in as'
                ]):
                    has_allauth_message = True
                    break
            
            # Si encontramos mensaje de allauth, reemplazarlo
            if has_allauth_message:
                # Limpiar TODOS los mensajes
                storage._queued_messages = []
                
                # Agregar nuestro mensaje personalizado
                display_name = self.format_user_name(request.user)
                
                # Determinar si es registro o login
                from django.utils import timezone
                import datetime
                
                if (timezone.now() - request.user.date_joined) < datetime.timedelta(seconds=30):
                    messages.success(request, format_html("¡Tu cuenta ha sido creada con éxito! Bienvenido, <strong>{}</strong>!", display_name))
                else:
                    messages.success(request, format_html("¡Bienvenido de nuevo, <strong>{}</strong>!", display_name))
        
        return response
    
    def format_user_name(self, user):
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