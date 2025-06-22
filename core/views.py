# core/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.utils.html import format_html
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from allauth.socialaccount.models import SocialAccount
from .forms import (
    SettingsForm, ProfileForm, CustomPasswordChangeForm,
    VerifyCodeForm, SetPasswordForm
)
from .models import UserSettings, PasswordSetupToken, UserProfile
from .utils import send_password_setup_email
from datetime import datetime
import unicodedata
import json
import pytz
from django.utils import timezone

@login_required
def home(request):
    from planner.models import Event, BloqueEstudio
    from planner.views import get_productividad_hoy
    from datetime import timedelta
    
    # Obtener zona horaria del usuario
    user_tz = get_user_timezone(request.user)
    
    # Obtener tareas del usuario para la semana actual
    today = timezone.now().astimezone(user_tz).date()
    now = timezone.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    # Filtrar eventos del usuario para la semana actual
    user_events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_week
    ).order_by('start_time')
    
    # Separar tareas por estado
    pending_tasks = user_events.filter(is_completed=False)
    completed_tasks = user_events.filter(is_completed=True)
    in_progress_tasks = pending_tasks.filter(start_time__lte=now, end_time__gte=now)
    
    # Obtener próximas entregas (tareas futuras no completadas)
    upcoming_tasks = Event.objects.filter(
        user=request.user,
        start_time__gte=now,  # Solo tareas futuras
        is_completed=False    # Solo tareas no completadas
    ).order_by('start_time')[:5]  # Limitar a las próximas 5 tareas
    
    # Organizar eventos por día de la semana para la vista semanal
    week_events = {i: [] for i in range(7)}  # 0=Lunes, 6=Domingo
    day_names_short = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    for event in user_events:
        event_local = event.start_time.astimezone(user_tz)
        day_of_week = event_local.weekday()
        
        # Determinar color según el tipo de evento
        color_class = 'purple'  # default
        if event.event_type == 'clase':
            color_class = 'blue'
        elif event.event_type == 'descanso':
            color_class = 'green'
        elif event.event_type == 'personal':
            color_class = 'orange'
        elif event.event_type == 'tarea':
            color_class = 'purple'
        
        week_events[day_of_week].append({
            'title': event.title,
            'start_time': event_local.strftime('%H:%M'),
            'end_time': event.end_time.astimezone(user_tz).strftime('%H:%M'),
            'color_class': color_class,
            'is_completed': event.is_completed
        })
    
    # Crear datos para los días de la semana
    week_days_data = []
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        week_days_data.append({
            'name': day_names_short[i],
            'date': current_day.day,
            'is_today': current_day == today,
            'events': week_events[i]
        })
    
    # Función para extraer materia del título
    def extract_subject_from_title(title):
        title_lower = title.lower().strip()
        subject_keywords = {
            'Matemáticas': ['matematicas', 'matemáticas', 'algebra', 'álgebra', 'calculo', 'cálculo'],
            'Física': ['fisica', 'física', 'mecanica', 'mecánica'],
            'Química': ['quimica', 'química', 'laboratorio'],
            'Programación': ['programacion', 'programación', 'codigo', 'código', 'python', 'javascript'],
            'Historia': ['historia'],
            'Inglés': ['ingles', 'inglés', 'english'],
            'Biología': ['biologia', 'biología'],
        }
        
        for subject, keywords in subject_keywords.items():
            if any(keyword in title_lower for keyword in keywords):
                return subject
        return 'General'
    
    # Preparar datos de próximas entregas con colores
    upcoming_tasks_data = []
    for task in upcoming_tasks:
        color_class = 'purple'  # default
        if task.event_type == 'clase':
            color_class = 'blue'
        elif task.event_type == 'descanso':
            color_class = 'green'
        elif task.event_type == 'personal':
            color_class = 'orange'
        elif task.event_type == 'tarea':
            color_class = 'purple'
        elif task.event_type == 'examen':
            color_class = 'red'
        elif task.event_type == 'proyecto':
            color_class = 'indigo'
        
        upcoming_tasks_data.append({
            'title': task.title,
            'start_time': task.start_time,
            'event_type': task.event_type,
            'color_class': color_class
        })
    
    # Obtener datos de productividad usando la función del planner
    productividad_hoy = get_productividad_hoy(request.user)
    
    # Calcular datos de productividad para la semana
    import calendar
    from datetime import timedelta
    from collections import defaultdict

    today = timezone.now().date()
    week_start = today - timedelta(days=today.weekday())

    # Obtener bloques de estudio completados para la semana
    bloques_semana = BloqueEstudio.objects.filter(
        usuario=request.user,
        fecha__range=(week_start, week_start + timedelta(days=6)),
        completado=True
    )

    # Obtener eventos completados para la semana
    eventos_completados = Event.objects.filter(
        user=request.user,
        start_time__date__range=(week_start, week_start + timedelta(days=6)),
        is_completed=True,
        event_type__in=['tarea', 'clase']
    )

    # Calcular productividad por día
    productividad_dias = [0] * 7
    meta_diaria = 120  # 2 horas en minutos

    # Agregar minutos de bloques de estudio
    for bloque in bloques_semana:
        index = bloque.fecha.weekday()
        productividad_dias[index] += bloque.duracion_min

    # Agregar minutos de eventos completados
    for evento in eventos_completados:
        fecha_evento = evento.start_time.date()
        if week_start <= fecha_evento <= week_start + timedelta(days=6):
            index = fecha_evento.weekday()
            duracion = (evento.end_time - evento.start_time).total_seconds() / 60
            productividad_dias[index] += int(duracion)

    # Convertir a porcentajes para el gráfico
    productivity_data = []
    day_names = ['L', 'M', 'M', 'J', 'V', 'S', 'D']
    
    for i in range(7):
        percentage = min(100, int((productividad_dias[i] / meta_diaria) * 100))
        productivity_data.append({
            'name': day_names[i],
            'percentage': percentage
        })
    
    # Debug: Imprimir datos de productividad
    print(f"🔍 Debug - Productividad por días (minutos): {productividad_dias}")
    print(f"🔍 Debug - Datos de productividad para gráfico: {productivity_data}")
    
    # Convertir datos a JSON para el template
    import json
    productivity_data_json = json.dumps(productivity_data)

    # Calcular estado de productividad
    if productividad_hoy >= 80:
        productivity_status = "Excelente"
    elif productividad_hoy >= 60:
        productivity_status = "Optimizado"
    elif productividad_hoy >= 40:
        productivity_status = "Regular"
    else:
        productivity_status = "Necesita mejora"
    
    context = {
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'in_progress_tasks': in_progress_tasks,
        'pending_count': pending_tasks.count(),
        'completed_count': completed_tasks.count(),
        'in_progress_count': in_progress_tasks.count(),
        'upcoming_tasks': upcoming_tasks_data,
        'week_days_data': week_days_data,
        'extract_subject': extract_subject_from_title,
        'productivity_data': productivity_data,
        'productivity_data_json': productivity_data_json,
        'productivity_status': productivity_status,
        'productividad_hoy': productividad_hoy,
    }
    
    # Agregar información del usuario y Google si está autenticado
    if request.user.is_authenticated:
        google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
        
        context.update({
            'user_display_name': format_user_name(request.user),
            'is_google_user': bool(google_account),
            'user_avatar': get_user_avatar(request.user),
        })
    
    return render(request, 'pages/home.html', context)

def normalize_text(text):
    """Normaliza el texto para manejar correctamente caracteres especiales"""
    if not text:
        return text
    
    # Normalizar Unicode y asegurar codificación correcta
    normalized = unicodedata.normalize('NFC', str(text))
    return normalized

def get_user_timezone(user):
    """Obtiene la zona horaria del usuario"""
    try:
        user_settings = UserSettings.objects.get(user=user)
        return pytz.timezone(user_settings.timezone)
    except (UserSettings.DoesNotExist, pytz.exceptions.UnknownTimeZoneError):
        # Zona horaria por defecto si no existe configuración
        return pytz.timezone('America/Guayaquil')

def get_greeting(user=None):
    """Devuelve el saludo apropiado según la hora del día en la zona horaria del usuario"""
    if user and user.is_authenticated:
        user_tz = get_user_timezone(user)
        now = timezone.now().astimezone(user_tz)
    else:
        # Para usuarios no autenticados, usar zona horaria por defecto
        default_tz = pytz.timezone('America/Guayaquil')
        now = timezone.now().astimezone(default_tz)
    
    hour = now.hour
    
    if 5 <= hour < 12:
        return "Buenos días"
    elif 12 <= hour < 19:
        return "Buenas tardes"
    else:
        return "Buenas noches"

def get_formatted_date(user=None):
    """Devuelve la fecha formateada en español en la zona horaria del usuario"""
    if user and user.is_authenticated:
        user_tz = get_user_timezone(user)
        now = timezone.now().astimezone(user_tz)
    else:
        # Para usuarios no autenticados, usar zona horaria por defecto
        default_tz = pytz.timezone('America/Guayaquil')
        now = timezone.now().astimezone(default_tz)
    
    # Nombres de días y meses en español
    days = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
              'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    day_name = days[now.weekday()]
    day_number = now.day
    month_name = months[now.month - 1]
    year = now.year
    
    # Agregar la hora
    hour = now.strftime('%H:%M')
    
    return f"{day_name}, {day_number} de {month_name} de {year} - {hour}"

def safe_title_case(text):
    """Aplica title case de forma segura con caracteres especiales"""
    if not text:
        return text
    
    # Normalizar primero
    text = normalize_text(text)
    
    # Dividir en palabras y capitalizar cada una
    words = []
    for word in text.split():
        if word:
            # Capitalizar la primera letra y mantener el resto en minúscula
            capitalized = word[0].upper() + word[1:].lower()
            words.append(capitalized)
    
    return ' '.join(words)

def format_user_name(user):
    """Función para formatear el nombre del usuario (primer nombre + primer apellido)"""
    if user.first_name and user.last_name:
        # Normalizar y dividir nombres y apellidos
        first_names = normalize_text(user.first_name).strip().split()
        last_names = normalize_text(user.last_name).strip().split()
        
        # Tomar solo el primer nombre y primer apellido
        first_name = safe_title_case(first_names[0]) if first_names else ""
        first_lastname = safe_title_case(last_names[0]) if last_names else ""
        
        return f"{first_name} {first_lastname}".strip()
    elif user.first_name:
        # Solo tiene first_name, usar solo el primer nombre
        first_names = normalize_text(user.first_name).strip().split()
        return safe_title_case(first_names[0]) if first_names else user.email
    else:
        # No tiene nombres, usar email
        return user.email.split('@')[0] if user.email else "Usuario"

def get_user_avatar(user):
    """Función para obtener el avatar del usuario (personalizado o de Google)"""
    # Primero verificar si tiene avatar personalizado
    try:
        profile = UserProfile.objects.get(user=user)
        if profile.avatar:
            return profile.avatar.url
    except UserProfile.DoesNotExist:
        pass
    
    # Si no tiene avatar personalizado, verificar si es usuario de Google
    google_account = SocialAccount.objects.filter(user=user, provider='google').first()
    if google_account and 'picture' in google_account.extra_data:
        return google_account.extra_data['picture']
    
    # Si no tiene ningún avatar, retornar None
    return None

@login_required
def perfil(request):
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    is_google_user = bool(google_account)
    user_has_password = request.user.has_usable_password()
    
    # Obtener o crear perfil del usuario
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Obtener o crear configuraciones del usuario
    user_settings, settings_created = UserSettings.objects.get_or_create(user=request.user)
    
    # Inicializar formularios - IMPORTANTE: pasar is_google_user al formulario
    profile_form = ProfileForm(instance=request.user, is_google_user=is_google_user)
    password_form = CustomPasswordChangeForm(request.user) if user_has_password else None
    
    # Procesamiento de formularios
    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'profile':
            # Pasar is_google_user también al procesar el POST
            profile_form = ProfileForm(request.POST, instance=request.user, is_google_user=is_google_user)
            
            # Solo procesar si no es usuario de Google
            if not is_google_user:
                if profile_form.is_valid():
                    # Guardar cambios
                    user = profile_form.save()
                    # Actualizar el username con el nuevo email si cambió
                    if user.email != user.username:
                        user.username = user.email
                        user.save()
                    
                    messages.success(request, format_html("¡Tu información personal ha sido actualizada exitosamente!"))
                    return redirect('core:perfil')
                else:
                    # Mostrar errores específicos
                    for field, errors in profile_form.errors.items():
                        for error in errors:
                            if field == '__all__':
                                messages.error(request, error)
                            else:
                                field_label = profile_form.fields[field].label if field in profile_form.fields else field.replace('_', ' ').title()
                                messages.error(request, f"{field_label}: {error}")
            else:
                messages.warning(request, "No puedes modificar tu información personal porque iniciaste sesión con Google.")
        
        elif form_type == 'password' and user_has_password:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Mantener la sesión activa después del cambio de contraseña
                update_session_auth_hash(request, user)
                messages.success(request, format_html("¡Tu contraseña ha sido cambiada exitosamente!"))
                return redirect('core:perfil')
            else:
                # Mostrar errores específicos
                for field, errors in password_form.errors.items():
                    for error in errors:
                        if field == '__all__':
                            messages.error(request, error)
                        else:
                            field_label = password_form.fields[field].label if field in password_form.fields else field.replace('_', ' ').title()
                            messages.error(request, f"{field_label}: {error}")

    context = {
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_display_name': format_user_name(request.user),
        'is_google_user': is_google_user,
        'user_has_password': user_has_password,
        'user_avatar': get_user_avatar(request.user),
        'profile_form': profile_form,
        'password_form': password_form,
        'user_settings': user_settings,
    }

    return render(request, 'pages/perfil.html', context)

@login_required
@require_http_methods(["POST"])
def upload_avatar(request):
    """Vista para subir foto de perfil vía AJAX"""
    try:
        if 'avatar' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se seleccionó ningún archivo'
            })
        
        avatar_file = request.FILES['avatar']
        
        # Validar tipo de archivo
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif']
        if avatar_file.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': 'Tipo de archivo no permitido. Solo se permiten JPG, PNG y GIF.'
            })
        
        # Validar tamaño (5MB máximo)
        if avatar_file.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 5MB.'
            })
        
        # Obtener o crear perfil del usuario
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Actualizar avatar
        user_profile.avatar = avatar_file
        user_profile.save()
        
        return JsonResponse({
            'success': True,
            'avatar_url': user_profile.avatar.url,
            'message': '¡Foto de perfil actualizada exitosamente!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al subir la imagen: {str(e)}'
        })

@login_required
@require_http_methods(["POST"])
def remove_avatar(request):
    """Vista para eliminar foto de perfil"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        
        if user_profile.avatar:
            # Eliminar archivo físico
            if user_profile.avatar.path:
                import os
                if os.path.isfile(user_profile.avatar.path):
                    os.remove(user_profile.avatar.path)
            
            # Limpiar campo de la base de datos
            user_profile.avatar = None
            user_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Foto de perfil eliminada exitosamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'No tienes una foto de perfil para eliminar'
            })
            
    except UserProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Perfil no encontrado'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Error al eliminar la imagen: {str(e)}'
        })

@login_required
def request_password_setup(request):
    """Vista para solicitar código de verificación para establecer contraseña"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Solo usuarios de Google sin contraseña pueden acceder
    if not google_account or request.user.has_usable_password():
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    if request.method == 'POST':
        # Invalidar tokens anteriores del usuario
        PasswordSetupToken.objects.filter(
            user=request.user,
            token_type='set_password',
            is_used=False
        ).update(is_used=True)
        
        # Crear nuevo token
        token = PasswordSetupToken.objects.create(
            user=request.user,
            token_type='set_password'
        )
        
        # Enviar email
        if send_password_setup_email(request.user, token):
            messages.success(request, format_html(
                "¡Código enviado! Revisa tu correo <strong>{}</strong> y ingresa el código de 6 dígitos.",
                request.user.email
            ))
            return redirect('core:verify_password_code')
        else:
            messages.error(request, "Hubo un error enviando el código. Por favor intenta de nuevo.")
    
    context = {
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_display_name': format_user_name(request.user),
        'user_avatar': get_user_avatar(request.user),
    }
    
    return render(request, 'pages/emails/request_password_setup.html', context)

@login_required
def verify_password_code(request):
    """Vista para verificar código de 6 dígitos"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Solo usuarios de Google sin contraseña pueden acceder
    if not google_account or request.user.has_usable_password():
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    form = VerifyCodeForm(user=request.user)
    
    if request.method == 'POST':
        form = VerifyCodeForm(user=request.user, data=request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Buscar y validar token
            token = PasswordSetupToken.objects.filter(
                user=request.user,
                token=code,
                token_type='set_password'
            ).first()
            
            if token and token.is_valid():
                # Guardar token en sesión para el siguiente paso
                request.session['verified_token_id'] = token.id
                messages.success(request, "¡Código verificado correctamente! Ahora establece tu contraseña.")
                return redirect('core:set_password')
            else:
                messages.error(request, "El código es inválido o ha expirado.")
    
    context = {
        'form': form,
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_display_name': format_user_name(request.user),
        'user_email': request.user.email,
        'user_avatar': get_user_avatar(request.user),
    }
    
    return render(request, 'pages/emails/verify_password_code.html', context)

@login_required
def set_password(request):
    """Vista para establecer nueva contraseña después de verificar código"""
    google_account = SocialAccount.objects.filter(user=request.user, provider='google').first()
    
    # Verificar permisos y token en sesión
    if (not google_account or 
        request.user.has_usable_password() or 
        'verified_token_id' not in request.session):
        messages.error(request, "No tienes permisos para acceder a esta página.")
        return redirect('core:perfil')
    
    # Verificar que el token siga siendo válido
    token = get_object_or_404(
        PasswordSetupToken,
        id=request.session['verified_token_id'],
        user=request.user,
        token_type='set_password'
    )
    
    if not token.is_valid():
        del request.session['verified_token_id']
        messages.error(request, "El código ha expirado. Solicita uno nuevo.")
        return redirect('core:request_password_setup')
    
    form = SetPasswordForm()
    
    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            # Establecer la nueva contraseña
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            
            # Marcar token como usado
            token.mark_as_used()
            
            # Limpiar sesión
            del request.session['verified_token_id']
            
            # Mantener la sesión activa
            update_session_auth_hash(request, request.user)
            
            messages.success(request, format_html(
                "¡Contraseña establecida correctamente! Ahora puedes usar tanto Google como tu contraseña para iniciar sesión."
            ))
            return redirect('core:perfil')
        else:
            # Mostrar errores específicos
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field.replace('_', ' ').title()
                    messages.error(request, f"{field_label}: {error}")
    
    context = {
        'form': form,
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_display_name': format_user_name(request.user),
        'user_avatar': get_user_avatar(request.user),
        'token': token,
    }
    
    return render(request, 'pages/emails/set_password.html', context)

@login_required
def settings(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')
        
        if form_type == 'notifications':
            # Actualizar preferencias de notificación
            user_settings.email_notifications = request.POST.get('email_notifications') == 'on'
            user_settings.task_reminders = request.POST.get('task_reminders') == 'on'
            user_settings.save()
            
            # Sincronizar con configuración de recordatorios
            try:
                from reminders.models import ReminderConfig
                reminder_config, created = ReminderConfig.objects.get_or_create(user=request.user)
                
                # Sincronizar configuraciones
                reminder_config.reminders_enabled = user_settings.task_reminders
                reminder_config.email_enabled = user_settings.email_notifications
                reminder_config.save()
                
                if created:
                    messages.info(request, "Se ha creado tu configuración de recordatorios automáticamente.")
                    
            except ImportError:
                # Si la app reminders no está disponible, continuar sin error
                pass
            
            messages.success(request, "¡Tus preferencias de notificación han sido actualizadas!")
            return redirect('core:perfil')
            
        elif form_type == 'settings':
            form = SettingsForm(request.POST)
            if form.is_valid():
                user_settings.language = form.cleaned_data['language']
                user_settings.timezone = form.cleaned_data['timezone']
                user_settings.save()
                messages.success(request, "¡Tus configuraciones han sido guardadas exitosamente!")
                return redirect('core:settings')
        else:
            messages.error(request, "Por favor corrige los errores en el formulario.")
    else:
        form = SettingsForm(initial={
            'language': user_settings.language,
            'timezone': user_settings.timezone
        })

    context = {
        'form': form,
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_avatar': get_user_avatar(request.user),
        'user_display_name': format_user_name(request.user),
    }

    return render(request, 'pages/settings.html', context)

@login_required
def get_current_datetime(request):
    """Vista AJAX para obtener fecha y hora actual del usuario"""
    try:
        data = {
            'greeting': get_greeting(request.user),
            'current_date': get_formatted_date(request.user),
            'success': True
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

@login_required
def weekly_view(request):
    """Vista para mostrar la vista semanal completa"""
    from planner.models import Event
    from datetime import timedelta
    
    # Obtener datos de la semana actual
    today = timezone.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    
    # Generar días de la semana
    week_days = []
    day_names = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
    
    for i in range(7):
        current_day = start_of_week + timedelta(days=i)
        week_days.append({
            'name': day_names[i],
            'date': current_day.day,
            'is_today': current_day == today
        })
    
    # Obtener eventos de la semana
    end_of_week = start_of_week + timedelta(days=6)
    events = Event.objects.filter(
        user=request.user,
        start_time__date__gte=start_of_week,
        start_time__date__lte=end_of_week
    ).order_by('start_time')
    
    # Formatear eventos para el template
    formatted_events = []
    for event in events:
        formatted_events.append({
            'title': event.title,
            'time': event.start_time.strftime('%H:%M'),
            'category': event.category if hasattr(event, 'category') else 'General',
            'type': 'task'
        })
    
    context = {
        'greeting': get_greeting(request.user),
        'current_date': get_formatted_date(request.user),
        'user_display_name': format_user_name(request.user),
        'user_avatar': get_user_avatar(request.user),
        'week_days': week_days,
        'events': formatted_events,
    }
    
    return render(request, 'pages/weekly_view.html', context)
