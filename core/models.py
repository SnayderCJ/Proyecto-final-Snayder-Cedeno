# core/models.py
from django.db import models
from django.contrib.auth.models import User
import random
import string
from django.utils import timezone
from datetime import timedelta

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=50, default='es')
    timezone = models.CharField(max_length=100, default='America/Guayaquil')

    def __str__(self):
        return f"Configuración de {self.user.username}"

class PasswordSetupToken(models.Model):
    """Modelo para tokens de establecimiento/cambio de contraseña"""
    
    TOKEN_TYPES = [
        ('set_password', 'Establecer Contraseña'),
        ('reset_password', 'Resetear Contraseña'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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