from core.views import get_greeting, get_formatted_date

def datetime_context(request):
    """Context processor para agregar fecha y saludo a todas las vistas"""
    context = {
        'greeting': get_greeting(request.user if request.user.is_authenticated else None),
        'current_date': get_formatted_date(request.user if request.user.is_authenticated else None),
    }
    return context
