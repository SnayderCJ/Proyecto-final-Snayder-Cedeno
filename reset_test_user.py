import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PLANIFICADOR_IA.settings')
django.setup()

from django.contrib.auth.models import User

# Obtener o crear el usuario de prueba
try:
    user = User.objects.get(username='testuser')
    # Establecer una contraseña conocida
    user.set_password('testuser123')
    user.save()
    print("Contraseña actualizada para el usuario testuser")
except User.DoesNotExist:
    # Crear el usuario si no existe
    User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testuser123'
    )
    print("Usuario testuser creado con la nueva contraseña")
