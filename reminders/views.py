# reminders/views.py - COMPLETO
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Reminder, ReminderConfiguration, ReminderLog
from .forms import ReminderForm, ReminderConfigurationForm
from .services.gmail_service import gmail_service
import json
import logging

logger = logging.getLogger(__name__)

@login_required
def reminder_list(request):
    """Lista todos los recordatorios del usuario"""
    reminders = Reminder.objects.filter(user=request.user).order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        reminders = reminders.filter(status=status_filter)
    
    # Paginación
    paginator = Paginator(reminders, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total': request.user.reminders.count(),
        'pending': request.user.reminders.filter(status='pending').count(),
        'sent': request.user.reminders.filter(status='sent').count(),
        'completed': request.user.reminders.filter(status='completed').count(),
        'cancelled': request.user.reminders.filter(status='cancelled').count(),
    }
    
    context = {
        'page_obj': page_obj,
        'reminders': page_obj,
        'status_filter': status_filter,
        'stats': stats,
    }
    return render(request, 'reminder_list.html', context)

@login_required
def create_reminder(request):
    """Crear nuevo recordatorio"""
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            
            # Obtener o crear configuración del usuario
            config, created = ReminderConfiguration.objects.get_or_create(user=request.user)
            
            # Log de creación
            ReminderLog.log_action(
                reminder=reminder,
                action='reminder_created',
                details=f'Recordatorio creado: {reminder.title}'
            )
            
            messages.success(request, f'✅ Recordatorio "{reminder.title}" creado exitosamente!')
            
            # Opción de envío inmediato de prueba
            if request.POST.get('send_test'):
                try:
                    if not gmail_service:
                        messages.error(request, '❌ Servicio de Gmail no disponible. Verifica tu configuración OAuth.')
                        return redirect('reminders:list')
                    
                    ai_subject = reminder.ai_subject or f'🧪 PRUEBA - {reminder.title}'
                    ai_description = reminder.ai_description or f"""
                    <p>Este es un recordatorio de prueba enviado desde tu Planificador IA.</p>
                    <p>Enviado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
                    <p>¡El sistema está funcionando correctamente! 🎉</p>
                    """
                    
                    create_calendar = config.calendar_enabled and reminder.reminder_type in ['calendar', 'both']
                    
                    result = gmail_service.send_reminder_email_with_calendar(
                        reminder=reminder,
                        ai_subject=ai_subject,
                        ai_description=ai_description,
                        create_calendar_event=create_calendar
                    )
                    
                    if result['success']:
                        messages.success(request, result.get('message', '📧 Recordatorio de prueba enviado!'))
                    else:
                        messages.warning(request, f'⚠️ Error al enviar: {result.get("error")}')
                        
                except Exception as e:
                    error_msg = f'❌ Error inesperado: {str(e)}'
                    messages.error(request, error_msg)
                    logger.error(f"Error en envío de prueba: {e}")
            
            return redirect('reminders:list')
    else:
        # Pre-llenar formulario con configuración del usuario
        config, created = ReminderConfiguration.objects.get_or_create(user=request.user)
        form = ReminderForm(initial={
            'reminder_type': config.preferred_type,
            'timing': config.default_timing,
        })
    
    context = {'form': form}
    return render(request, 'create_reminder.html', context)


@login_required
def reminder_configuration(request):
    """Configurar recordatorios del usuario"""
    config, created = ReminderConfiguration.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = ReminderConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, '⚙️ Configuración guardada exitosamente!')
            
            # NO CREAR LOG para configuración (porque reminder_id es requerido)
            # Solo mostrar mensaje de éxito
            
            return redirect('reminders:configuration')
    else:
        form = ReminderConfigurationForm(instance=config)
    
    # Estadísticas del usuario
    stats = {
        'total': request.user.reminders.count(),
        'pending': request.user.reminders.filter(status='pending').count(),
        'sent': request.user.reminders.filter(status='sent').count(),
        'completed': request.user.reminders.filter(status='completed').count(),
        'cancelled': request.user.reminders.filter(status='cancelled').count(),
        'failed': request.user.reminders.filter(status='failed').count(),
    }
    
    # Logs recientes (solo de recordatorios, no de configuración)
    recent_logs = ReminderLog.objects.filter(
        reminder__user=request.user
    ).select_related('reminder').order_by('-timestamp')[:10]
    
    context = {
        'form': form,
        'config': config,
        'stats': stats,
        'recent_logs': recent_logs,
    }
    return render(request, 'configuration.html', context)

def respond_reminder(request, reminder_id, action):
    """Responder a recordatorios desde email - NO requiere login"""
    reminder = get_object_or_404(Reminder, id=reminder_id)
    
    valid_actions = ['completed', 'snooze', 'cancel']
    if action not in valid_actions:
        return HttpResponse('❌ Acción inválida', status=400)
    
    user_name = reminder.get_user_full_name()
    message = ''
    
    if action == 'completed':
        reminder.mark_as_responded('completed')
        message = f'✅ Recordatorio "{reminder.title}" marcado como completado.'
        ReminderLog.log_action(
            reminder=reminder,
            action='user_response_completed',
            details='Usuario marcó como completado desde email'
        )
        
    elif action == 'snooze':
        # Posponer 15 minutos
        reminder.scheduled_send_time = timezone.now() + timezone.timedelta(minutes=15)
        reminder.status = 'pending'
        reminder.save()
        message = f'⏰ Recordatorio "{reminder.title}" pospuesto 15 minutos.'
        ReminderLog.log_action(
            reminder=reminder,
            action='user_response_snooze',
            details='Usuario pospuso recordatorio 15 minutos desde email'
        )
        
    elif action == 'cancel':
        reminder.status = 'cancelled'
        reminder.save()
        message = f'❌ Recordatorio "{reminder.title}" cancelado.'
        ReminderLog.log_action(
            reminder=reminder,
            action='user_response_cancel',
            details='Usuario canceló recordatorio desde email'
        )
    
    # Página de respuesta elegante
    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Recordatorio Actualizado - Planificador IA</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{
                background: white;
                padding: 3rem;
                border-radius: 15px;
                text-align: center;
                box-shadow: 0 20px 40px rgba(0,0,0,0.2);
                max-width: 500px;
                margin: 1rem;
            }}
            h1 {{ 
                color: #333; 
                margin-bottom: 1rem; 
                font-size: 1.5rem;
            }}
            p {{ 
                color: #666; 
                line-height: 1.6; 
                margin: 1rem 0;
            }}
            .icon {{ 
                font-size: 4rem; 
                margin-bottom: 1rem; 
            }}
            .user-info {{ 
                background: #f8f9fa; 
                padding: 1rem; 
                border-radius: 8px; 
                margin: 1rem 0; 
                font-size: 0.9rem;
                color: #555;
            }}
            .back-link {{
                display: inline-block;
                margin-top: 1rem;
                padding: 0.5rem 1rem;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                transition: background 0.3s;
            }}
            .back-link:hover {{
                background: #5a6fd8;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">
                {'✅' if action == 'completed' else '⏰' if action == 'snooze' else '❌'}
            </div>
            <h1>{message}</h1>
            <div class="user-info">
                <strong>👤 Usuario:</strong> {user_name}<br>
                <strong>📅 Fecha:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}<br>
                <strong>🆔 ID:</strong> {str(reminder.id)[:8]}...
            </div>
            <p>Tu respuesta ha sido registrada exitosamente en el sistema.</p>
            <p>El cambio se ha aplicado inmediatamente.</p>
            <a href="#" onclick="window.close()" class="back-link">
                🔙 Cerrar ventana
            </a>
        </div>
    </body>
    </html>
    """
    
    return HttpResponse(html_response)

@login_required
@require_http_methods(["POST"])
def test_send_reminder(request, reminder_id):
    """Enviar recordatorio de prueba - AJAX endpoint"""
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
        
        # Verificar si Gmail service está disponible
        if not gmail_service:
            return JsonResponse({
                'success': False,
                'message': '❌ Servicio de Gmail no disponible. Verifica tu configuración OAuth.'
            })
        
        # Obtener o crear configuración
        config = getattr(request.user, 'reminder_config', None)
        if not config:
            config = ReminderConfiguration.objects.create(user=request.user)
        
        # Verificaciones previas
        if not config.reminders_enabled:
            return JsonResponse({
                'success': False,
                'message': '⚠️ Tienes los recordatorios desactivados en tu configuración.'
            })
        
        if not request.user.email:
            return JsonResponse({
                'success': False,
                'message': '❌ Tu cuenta no tiene email configurado. Verifica tu autenticación OAuth.'
            })
        
        # Preparar contenido de prueba
        ai_subject = reminder.ai_subject or f'🧪 PRUEBA - {reminder.title}'
        ai_description = reminder.ai_description or f"""
        <div style="background: #e3f2fd; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3 style="margin: 0 0 10px 0; color: #1976d2;">🧪 Recordatorio de Prueba</h3>
            <p style="margin: 0;">Este es un recordatorio de prueba enviado desde tu Planificador IA.</p>
            <p style="margin: 10px 0 0 0;"><strong>Enviado:</strong> {timezone.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <p style="margin: 0;"><strong>📊 Tu configuración actual:</strong></p>
            <ul style="margin: 10px 0;">
                <li>📧 Email: {'✅ Activo' if config.email_enabled else '❌ Desactivado'}</li>
                <li>📅 Calendar: {'✅ Activo' if config.calendar_enabled else '❌ Desactivado'}</li>
                <li>🔔 Tipo: {reminder.get_reminder_type_display()}</li>
                <li>⏰ Frecuencia: {config.get_current_frequency_display()}</li>
            </ul>
            <p style="margin: 10px 0 0 0;">¡El sistema está funcionando correctamente! 🎉</p>
        </div>
        """
        
        # Determinar si crear evento de calendario
        create_calendar = (
            config.calendar_enabled and 
            reminder.reminder_type in ['calendar', 'both']
        )
        
        # Enviar recordatorio
        result = gmail_service.send_reminder_email_with_calendar(
            reminder=reminder,
            ai_subject=ai_subject,
            ai_description=ai_description,
            create_calendar_event=create_calendar
        )
        
        # Log del envío de prueba
        ReminderLog.log_action(
            reminder=reminder,
            action='test_send_success' if result['success'] else 'test_send_error',
            details=f'Envío de prueba desde panel: {result.get("message", "")}',
            success=result['success'],
            error_message=result.get('error', '') if not result['success'] else ''
        )
        
        return JsonResponse(result)
        
    except Exception as e:
        error_msg = f'❌ Error inesperado: {str(e)}'
        logger.error(f"Error en test_send_reminder: {e}")
        
        # Log del error
        try:
            ReminderLog.log_action(
                reminder=reminder,
                action='test_send_error',
                details=f'Error en envío de prueba: {str(e)}',
                success=False,
                error_message=str(e)
            )
        except:
            pass
        
        return JsonResponse({
            'success': False,
            'message': error_msg
        })

@login_required
@require_http_methods(["POST"])
def toggle_reminder_status(request, reminder_id):
    """Cambiar estado de recordatorio - AJAX endpoint"""
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
        
        if reminder.status == 'pending':
            reminder.status = 'cancelled'
            message = f'❌ Recordatorio "{reminder.title}" cancelado'
            action = 'manual_cancel'
        elif reminder.status in ['cancelled', 'failed']:
            reminder.status = 'pending'
            reminder.calculate_send_time()  # Recalcular tiempo de envío
            message = f'🔄 Recordatorio "{reminder.title}" reactivado'
            action = 'manual_reactivate'
        else:
            return JsonResponse({
                'success': False,
                'message': '⚠️ No se puede cambiar el estado de este recordatorio'
            })
        
        reminder.save()
        
        # Log del cambio
        ReminderLog.log_action(
            reminder=reminder,
            action=action,
            details=f'Estado cambiado manualmente a: {reminder.status}'
        )
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_status': reminder.status
        })
        
    except Exception as e:
        logger.error(f"Error en toggle_reminder_status: {e}")
        return JsonResponse({
            'success': False,
            'message': f'❌ Error: {str(e)}'
        })
        



@login_required
@require_http_methods(["POST"])
def toggle_reminder_status(request, reminder_id):
    """Cambiar estado de recordatorio - AJAX endpoint"""
    try:
        reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
        
        if reminder.status == 'pending':
            reminder.status = 'cancelled'
            message = f'❌ Recordatorio "{reminder.title}" cancelado'
            action = 'manual_cancel'
        elif reminder.status in ['cancelled', 'failed']:
            reminder.status = 'pending'
            reminder.calculate_send_time()  # Recalcular tiempo de envío
            message = f'🔄 Recordatorio "{reminder.title}" reactivado'
            action = 'manual_reactivate'
        else:
            return JsonResponse({
                'success': False,
                'message': '⚠️ No se puede cambiar el estado de este recordatorio'
            })
        
        reminder.save()
        
        # Log del cambio (opcional - sin recordatorio específico para evitar error)
        try:
            ReminderLog.log_action(
                reminder=reminder,
                action=action,
                details=f'Estado cambiado manualmente a: {reminder.status}'
            )
        except:
            pass  # Ignorar errores de log
        
        return JsonResponse({
            'success': True,
            'message': message,
            'new_status': reminder.status
        })
        
    except Exception as e:
        logger.error(f"Error en toggle_reminder_status: {e}")
        return JsonResponse({
            'success': False,
            'message': f'❌ Error: {str(e)}'
        })