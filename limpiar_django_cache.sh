#!/bin/bash
# Usar en la consola de git bash


echo "💡 Limpiando caché de Django..."

# Ejecuta el shell de Django y borra el caché configurado
python manage.py shell << END
from django.core.cache import cache
cache.clear()
print("✅ Caché de Django limpiado.")
END

echo "🧹 Eliminando archivos .pyc y carpetas __pycache__..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -exec rm -r {} + 

# (Opcional) Descomenta para borrar migraciones (cuidado si ya tienes migraciones importantes)
# echo "🗑️ Borrando archivos de migraciones..."
# find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
# find . -path "*/migrations/*.pyc"  -delete

echo "✅ Todo limpio. Proyecto listo."
