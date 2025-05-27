from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
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