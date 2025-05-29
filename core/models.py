# core/models.py
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta
import os
from PIL import Image

def user_avatar_path(instance, filename):
    """Función para generar la ruta donde se guardarán las fotos de perfil"""
    # Obtener la extensión del archivo
    ext = filename.split('.')[-1]
    # Generar nombre único
    filename = f"avatar_{instance.user.id}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
    # Retornar la ruta completa
    return f'profile_photos/{filename}'

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='core_settings')
    language = models.CharField(max_length=50, default='es')
    timezone = models.CharField(max_length=100, default='America/Guayaquil')

    def __str__(self):
        return f"Configuración de {self.user.username}"
    
    class Meta:
        verbose_name = "Configuración de Usuario"
        verbose_name_plural = "Configuraciones de Usuario"

class UserProfile(models.Model):
    """Modelo para información adicional del perfil del usuario"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        help_text="Foto de perfil del usuario"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def save(self, *args, **kwargs):
        # Eliminar foto anterior si existe
        if self.pk:
            try:
                old_avatar = UserProfile.objects.get(pk=self.pk).avatar
                if old_avatar and old_avatar != self.avatar:
                    if os.path.isfile(old_avatar.path):
                        os.remove(old_avatar.path)
            except UserProfile.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Redimensionar imagen si es necesario
        if self.avatar:
            self.resize_avatar()
    
    def resize_avatar(self):
        """Redimensiona la imagen de perfil a un tamaño estándar"""
        try:
            img = Image.open(self.avatar.path)
            
            # Convertir a RGB si es necesario
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionar manteniendo proporción
            max_size = (300, 300)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Guardar imagen redimensionada
            img.save(self.avatar.path, optimize=True, quality=85)
            
        except Exception as e:
            print(f"Error redimensionando imagen: {e}")
    
    def get_avatar_url(self):
        """Obtiene la URL del avatar del usuario"""
        if self.avatar:
            return self.avatar.url
        return None
    
    @classmethod
    def get_user_avatar(cls, user):
        """Método estático para obtener el avatar de un usuario"""
        try:
            profile = cls.objects.get(user=user)
            return profile.get_avatar_url()
        except cls.DoesNotExist:
            return None
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

class PasswordSetupToken(models.Model):
    """Modelo para tokens de establecimiento/cambio de contraseña"""
    
    TOKEN_TYPES = [
        ('set_password', 'Establecer Contraseña'),
        ('reset_password', 'Resetear Contraseña'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_tokens')
    token = models.CharField(max_length=6, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES, default='set_password')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        if not self.expires_at:
            # Token válido por 15 minutos
            self.expires_at = timezone.now() + timedelta(minutes=15)
        super().save(*args, **kwargs)
    
    def generate_token(self):
        """Genera un código de 6 dígitos único"""
        while True:
            token = ''.join(random.choices(string.digits, k=6))
            if not PasswordSetupToken.objects.filter(token=token, is_used=False).exists():
                return token
    
    def is_valid(self):
        """Verifica si el token es válido"""
        return (
            not self.is_used and 
            timezone.now() <= self.expires_at
        )
    
    def mark_as_used(self):
        """Marca el token como usado"""
        self.is_used = True
        self.used_at = timezone.now()
        self.save()
    
    def __str__(self):
        return f"Token {self.token} para {self.user.username} ({self.get_token_type_display()})"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Token de Contraseña"
        verbose_name_plural = "Tokens de Contraseña"