from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.utils.html import format_html

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
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
    
    def save_user(self, request, sociallogin, form=None):
        """Personalizar cómo se guarda el usuario de Google"""
        user = super().save_user(request, sociallogin, form)
        
        # Procesar y capitalizar nombres
        if user.first_name:
            # Capitalizar cada nombre
            names = user.first_name.strip().split()
            user.first_name = " ".join([name.title() for name in names])
        
        if user.last_name:
            # Capitalizar cada apellido
            surnames = user.last_name.strip().split()
            user.last_name = " ".join([surname.title() for surname in surnames])
        
        user.save()
        return user
    
    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        """Personalizar mensajes de error"""
        messages.error(request, "Hubo un problema con la autenticación de Google. Inténtalo de nuevo.")
    
    def pre_social_login(self, request, sociallogin):
        """Se ejecuta antes del login social"""
        pass
    
    def populate_user(self, request, sociallogin, data):
        """Personalizar cómo se popula el usuario con datos de Google"""
        user = super().populate_user(request, sociallogin, data)
        
        # Asegurar que los nombres tengan la capitalización correcta
        if user.first_name:
            names = user.first_name.strip().split()
            user.first_name = " ".join([name.title() for name in names])
        
        if user.last_name:
            surnames = user.last_name.strip().split()
            user.last_name = " ".join([surname.title() for surname in surnames])
            
        return user