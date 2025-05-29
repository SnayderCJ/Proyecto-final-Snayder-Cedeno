from django.contrib import messages
from django.utils.html import format_html
import unicodedata

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
            
            # VERIFICAR SI YA HAY UN MENSAJE DE REGISTRO/LOGIN MANUAL
            has_manual_message = False
            for message in messages_list:
                message_text = str(message.message).lower()
                if any(phrase in message_text for phrase in [
                    'tu cuenta ha sido creada',
                    'bienvenido de nuevo',
                    'cuenta creada con éxito',
                    'perfecto! hemos conectado'
                ]):
                    has_manual_message = True
                    break
            
            # SI YA HAY MENSAJE MANUAL, NO INTERFERIR
            if has_manual_message:
                return response
            
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
                
                # Determinar si es registro o login por tiempo
                from django.utils import timezone
                import datetime
                
                if (timezone.now() - request.user.date_joined) < datetime.timedelta(seconds=30):
                    # USAR format_html PARA RENDERIZAR HTML CORRECTAMENTE
                    messages.success(
                        request, 
                        format_html("¡Tu cuenta ha sido creada con éxito! Bienvenido, <strong>{}</strong>!", display_name)
                    )
                else:
                    # USAR format_html PARA RENDERIZAR HTML CORRECTAMENTE
                    messages.success(
                        request, 
                        format_html("¡Bienvenido de nuevo, <strong>{}</strong>!", display_name)
                    )
        
        return response
    
    def normalize_text(self, text):
        """Normaliza el texto para manejar correctamente caracteres especiales"""
        if not text:
            return text
        
        # Normalizar Unicode y asegurar codificación correcta
        normalized = unicodedata.normalize('NFC', str(text))
        return normalized

    def safe_title_case(self, text):
        """Aplica title case de forma segura con caracteres especiales"""
        if not text:
            return text
        
        # Normalizar primero
        text = self.normalize_text(text)
        
        # Dividir en palabras y capitalizar cada una
        words = []
        for word in text.split():
            if word:
                # Capitalizar la primera letra y mantener el resto en minúscula
                capitalized = word[0].upper() + word[1:].lower()
                words.append(capitalized)
        
        return ' '.join(words)
    
    def format_user_name(self, user):
        """Función para formatear el nombre del usuario"""
        if user.first_name and user.last_name:
            # Normalizar y dividir nombres y apellidos
            first_names = self.normalize_text(user.first_name).strip().split()
            last_names = self.normalize_text(user.last_name).strip().split()
            
            # Tomar solo el primer nombre y primer apellido
            first_name = self.safe_title_case(first_names[0]) if first_names else ""
            first_lastname = self.safe_title_case(last_names[0]) if last_names else ""
            
            return f"{first_name} {first_lastname}".strip()
        elif user.first_name:
            # Solo tiene first_name, usar solo el primer nombre
            first_names = self.normalize_text(user.first_name).strip().split()
            return self.safe_title_case(first_names[0]) if first_names else user.email
        else:
            # No tiene nombres, usar email
            return user.email.split('@')[0] if user.email else "Usuario"