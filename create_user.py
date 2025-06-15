import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PLANIFICADOR_IA.settings')
django.setup()

from django.contrib.auth.models import User

try:
    user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print('Usuario creado exitosamente')
except Exception as e:
    print(f'Error: {e}')
