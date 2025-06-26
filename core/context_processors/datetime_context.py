from datetime import datetime
import pytz
from django.conf import settings

def datetime_context(request):
    """Context processor para agregar información de fecha y hora a todos los templates"""
    # Obtener la zona horaria configurada o usar la predeterminada
    timezone = pytz.timezone(settings.TIME_ZONE)
    now = datetime.now(timezone)
    
    # Determinar el saludo según la hora del día
    hour = now.hour
    if 5 <= hour < 12:
        greeting = "Buenos días"
    elif 12 <= hour < 19:
        greeting = "Buenas tardes"
    else:
        greeting = "Buenas noches"
    
    # Formatear la fecha en español
    months_es = {
        'January': 'enero',
        'February': 'febrero',
        'March': 'marzo',
        'April': 'abril',
        'May': 'mayo',
        'June': 'junio',
        'July': 'julio',
        'August': 'agosto',
        'September': 'septiembre',
        'October': 'octubre',
        'November': 'noviembre',
        'December': 'diciembre'
    }
    
    # Formatear la fecha
    date_str = now.strftime('%d de %B de %Y')
    for en, es in months_es.items():
        date_str = date_str.replace(en, es)
    
    return {
        'current_date': date_str,
        'greeting': greeting,
    }
