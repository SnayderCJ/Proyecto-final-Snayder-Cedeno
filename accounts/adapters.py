from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.signals import pre_social_login
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html
from django.dispatch import receiver
import unicodedata
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adaptador personalizado para manejar login social"""
    
    def get_login_redirect_url(self, request):
        """Personalizar redirección después del login"""
        return "/"
    
    def get_signup_redirect_url(self, request):
        """Personalizar redirección después del registro"""
        return "/"
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Manejar errores de autenticación social"""
        # Redirigir a nuestra vista personalizada de cancelación
        return redirect('accounts:social_login_cancelled')
    
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
    
    def pre_social_login(self, request, sociallogin):
        """
        Invocado justo después de que un usuario se conecta exitosamente
        vía un proveedor social, pero antes de que la cuenta sea guardada.
        
        Aquí manejamos el caso donde un usuario intenta hacer login social
        con un email que ya existe en el sistema.
        """
        # Solo procesar si no es un login existente
        if sociallogin.is_existing:
            return
            
        # Verificar si ya existe un usuario con ese email
        if sociallogin.user.email:
            try:
                existing_user = User.objects.get(email__iexact=sociallogin.user.email)
                
                # Conectar la cuenta social al usuario existente
                sociallogin.connect(request, existing_user)
                
                # Formatear nombre para el mensaje
                display_name = self.format_user_name(existing_user)
                
                # Agregar mensaje informativo usando sesión para que persista
                request.session['social_connect_message'] = format_html(
                    "¡Perfecto! Hemos conectado tu cuenta de Google con tu cuenta existente. "
                    "¡Bienvenido de nuevo, <strong>{}</strong>!",
                    display_name
                )
                
                logger.info(f"Conectada cuenta social para usuario existente: {existing_user.email}")
                
            except User.DoesNotExist:
                # No existe usuario con ese email, puede proceder normalmente
                logger.info(f"Nuevo usuario social: {sociallogin.user.email}")
                pass
            except Exception as e:
                # Log del error pero no interrumpir el flujo
                logger.error(f"Error en pre_social_login: {e}")
                pass
    
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
    
    def save_user(self, request, sociallogin, form=None):
        """
        Guarda un usuario recién registrado y devuelve el usuario.
        Personalizar cómo se guarda el usuario de Google
        """
        try:
            user = super().save_user(request, sociallogin, form)
            
            # Extraer y procesar nombres del perfil social
            if sociallogin.account.provider == 'google':
                extra_data = sociallogin.account.extra_data
                
                # Procesar first_name
                if not user.first_name and 'given_name' in extra_data:
                    names = self.normalize_text(extra_data['given_name']).strip().split()
                    processed_names = [self.safe_title_case(name) for name in names]
                    user.first_name = " ".join(processed_names)
                
                # Procesar last_name
                if not user.last_name and 'family_name' in extra_data:
                    surnames = self.normalize_text(extra_data['family_name']).strip().split()
                    processed_surnames = [self.safe_title_case(surname) for surname in surnames]
                    user.last_name = " ".join(processed_surnames)
                
                # Si no tiene nombres pero tiene 'name' completo
                if not user.first_name and not user.last_name and 'name' in extra_data:
                    full_name = self.normalize_text(extra_data['name']).strip()
                    names = full_name.split()
                    if len(names) >= 2:
                        # Dividir en nombres y apellidos
                        middle_point = len(names) // 2
                        first_names = names[:middle_point]
                        last_names = names[middle_point:]
                        
                        processed_first = [self.safe_title_case(name) for name in first_names]
                        processed_last = [self.safe_title_case(name) for name in last_names]
                        
                        user.first_name = " ".join(processed_first)
                        user.last_name = " ".join(processed_last)
                    elif len(names) == 1:
                        user.first_name = self.safe_title_case(names[0])
                
                user.save()
            
            return user
            
        except Exception as e:
            logger.error(f"Error en save_user: {e}")
            # Si hay error, devolver usuario tal como está
            return super().save_user(request, sociallogin, form)
    
    def populate_user(self, request, sociallogin, data):
        """
        Personalizar cómo se popula el usuario con datos de Google
        """
        try:
            user = super().populate_user(request, sociallogin, data)
            
            # Asegurar que los nombres tengan la capitalización correcta
            if user.first_name:
                names = self.normalize_text(user.first_name).strip().split()
                processed_names = [self.safe_title_case(name) for name in names]
                user.first_name = " ".join(processed_names)
            
            if user.last_name:
                surnames = self.normalize_text(user.last_name).strip().split()
                processed_surnames = [self.safe_title_case(surname) for surname in surnames]
                user.last_name = " ".join(processed_surnames)
                
            return user
            
        except Exception as e:
            logger.error(f"Error en populate_user: {e}")
            return super().populate_user(request, sociallogin, data)

class CustomAccountAdapter(DefaultAccountAdapter):
    """Adaptador personalizado para cuentas regulares"""
    
    def add_message(self, request, level, message_template, message_context=None, extra_tags='', fail_silently=False, *args, **kwargs):
        """
        Personalizar mensajes de allauth
        """
        try:
            # Filtrar mensajes que no queremos mostrar
            message_str = str(message_template).lower()
            
            # Evitar mensajes duplicados o innecesarios
            if any(phrase in message_str for phrase in [
                'successfully signed in',
                'ha iniciado sesión exitosamente',
                'logged in as'
            ]):
                # No agregar estos mensajes, los manejamos en el middleware
                return
            
            # Para otros mensajes, usar el comportamiento por defecto
            super().add_message(request, level, message_template, message_context, extra_tags, fail_silently, *args, **kwargs)
            
        except Exception as e:
            logger.error(f"Error en add_message: {e}")
            if not fail_silently:
                raise
