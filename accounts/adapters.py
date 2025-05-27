from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import unicodedata

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
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
    
    def save_user(self, request, sociallogin, form=None):
        """Personalizar cómo se guarda el usuario de Google"""
        user = super().save_user(request, sociallogin, form)
        
        # Procesar y capitalizar nombres con caracteres especiales
        if user.first_name:
            # Normalizar y capitalizar cada nombre
            names = self.normalize_text(user.first_name).strip().split()
            processed_names = [self.safe_title_case(name) for name in names]
            user.first_name = " ".join(processed_names)
        
        if user.last_name:
            # Normalizar y capitalizar cada apellido
            surnames = self.normalize_text(user.last_name).strip().split()
            processed_surnames = [self.safe_title_case(surname) for surname in surnames]
            user.last_name = " ".join(processed_surnames)
        
        user.save()
        return user
    
    def populate_user(self, request, sociallogin, data):
        """Personalizar cómo se popula el usuario con datos de Google"""
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