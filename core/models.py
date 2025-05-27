from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
   user = models.OneToOneField(User, on_delete=models.CASCADE)
   language = models.CharField(max_length=50, default='es')
   timezone = models.CharField(max_length=100, default='America/Guayaquil')

   def __str__(self):
      return f"Configuración de {self.user.username}"