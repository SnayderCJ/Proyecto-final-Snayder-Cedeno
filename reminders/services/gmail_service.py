# reminders/services/gmail_service.py - FINAL CORREGIDO
import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from django.contrib.auth.models import User
import logging

logger = logging.getLogger(__name__)

class GmailService:
    """Servicio Gmail integrado con OAuth - FINAL CORREGIDO"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar'
    ]
    
    def __init__(self):
        self.gmail_service = None
        self.calendar_service = None
        try:
            self._authenticate()
        except Exception as e:
            print(f"ERROR: Error al inicializar Gmail Service: {str(e)}")
            logger.error(f"Gmail Service initialization failed: {str(e)}")
    
    def _authenticate(self):
        """Autenticación OAuth"""
        try:
            creds = None
            
            token_path = os.path.join(settings.BASE_DIR, 'token.json')
            credentials_path = os.path.join(settings.BASE_DIR, 'studiFly_desktop_client.json')
            
            print(f"INFO: Buscando token en: {token_path}")
            print(f"INFO: Buscando credenciales en: {credentials_path}")
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
                print("INFO: Token encontrado")
            else:
                print("WARNING: Token no encontrado")
            
            # Verificar si los scopes son correctos
            if creds and creds.valid:
                current_scopes = getattr(creds, 'scopes', [])
                required_scopes = set(self.SCOPES)
                current_scopes_set = set(current_scopes) if current_scopes else set()
                
                if not required_scopes.issubset(current_scopes_set):
                    print("WARNING: Scopes insuficientes en token actual")
                    print(f"INFO: Scopes requeridos: {self.SCOPES}")
                    print(f"INFO: Scopes actuales: {current_scopes}")
                    creds = None
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    print("INFO: Intentando refrescar token...")
                    try:
                        creds.refresh(Request())
                        print("SUCCESS: Token refrescado")
                    except Exception as refresh_error:
                        print(f"ERROR: No se pudo refrescar token: {refresh_error}")
                        creds = None
                
                if not creds:
                    if os.path.exists(credentials_path):
                        print("INFO: Iniciando flujo OAuth con nuevos scopes...")
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                        creds = flow.run_local_server(
                            port=0,
                            prompt='consent'
                        )
                        print("SUCCESS: OAuth completado con nuevos scopes")
                    else:
                        raise FileNotFoundError(f"ERROR: No se encontró {credentials_path}")
                
                # Guardar credenciales actualizadas
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
                print("INFO: Token guardado con nuevos scopes")
            
            # Crear servicios
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
            # Verificar conexión
            try:
                profile = self.gmail_service.users().getProfile(userId='me').execute()
                email = profile.get('emailAddress')
                print(f"SUCCESS: Gmail conectado: {email}")
                
                calendars = self.calendar_service.calendarList().list().execute()
                count = len(calendars.get('items', []))
                print(f"SUCCESS: Calendar conectado: {count} calendarios")
                
                logger.info("Google services authenticated successfully")
                
            except Exception as verify_error:
                print(f"ERROR: Verificación de servicios falló: {verify_error}")
                raise
            
        except Exception as e:
            error_msg = f"ERROR: Error en autenticación OAuth: {str(e)}"
            print(error_msg)
            logger.error(f"OAuth authentication failed: {str(e)}")
            raise
    
    def send_reminder_email_with_calendar(self, reminder, ai_subject=None, ai_description=None, create_calendar_event=True):
        """Envía recordatorio por email y opcionalmente crea evento en Google Calendar"""
        try:
            user = reminder.user
            
            # Verificar email del usuario
            if not user.email:
                raise ValueError(f"Usuario {user.username} no tiene email configurado")
            
            print(f"INFO: Enviando email a: {user.email}")
            
            # Nombre del usuario
            user_name = f"{user.first_name} {user.last_name}".strip() or user.username
            
            # Generar contenido del email
            email_content = self._generate_email_content(
                reminder, 
                user_name, 
                ai_subject, 
                ai_description
            )
            
            # Crear evento en Google Calendar si se solicita
            calendar_event_id = None
            calendar_link = None
            if create_calendar_event and self.calendar_service:
                print("INFO: Creando evento en Google Calendar...")
                calendar_event_id, calendar_link = self._create_calendar_event(
                    reminder, 
                    user_name, 
                    ai_subject, 
                    ai_description
                )
                if calendar_event_id:
                    print(f"SUCCESS: Evento creado: {calendar_event_id}")
                    # Agregar link de calendario al contexto del email
                    email_content['calendar_link'] = calendar_link
                    # Regenerar email con link de calendario
                    email_content = self._generate_email_content(
                        reminder, 
                        user_name, 
                        ai_subject, 
                        ai_description,
                        calendar_link
                    )
            
            # Crear y enviar mensaje
            message = self._create_message(
                to_email=user.email,
                subject=email_content['subject'],
                html_content=email_content['html'],
                reminder=reminder
            )
            
            print("INFO: Enviando email...")
            result = self.gmail_service.users().messages().send(
                userId='me', 
                body=message
            ).execute()
            
            # Actualizar recordatorio
            reminder.mark_as_sent()
            reminder.email_message_id = result.get('id', '')
            if calendar_event_id:
                reminder.calendar_event_id = calendar_event_id
            reminder.save()
            
            success_msg = f"SUCCESS: Email enviado a {user.email}"
            print(success_msg)
            logger.info(success_msg)
            
            return {
                'success': True,
                'email_id': result.get('id', ''),
                'calendar_event_id': calendar_event_id,
                'calendar_link': calendar_link,
                'message': f'Email enviado a {user.email}' + (
                    ' + Evento en Calendar' if calendar_event_id else ''
                )
            }
            
        except Exception as e:
            error_msg = f"ERROR: Error al enviar recordatorio {reminder.id}: {str(e)}"
            print(error_msg)
            logger.error(error_msg)
            
            reminder.last_error = str(e)
            reminder.send_attempts += 1
            reminder.status = 'failed'
            reminder.save()
            
            return {
                'success': False, 
                'error': str(e),
                'message': f'Error: {str(e)}'
            }
    
    def _create_calendar_event(self, reminder, user_name, ai_subject=None, ai_description=None):
        """Crea evento en Google Calendar"""
        try:
            subject = ai_subject or f"Recordatorio: {reminder.title}"
            description = ai_description or reminder.description or "Recordatorio automático"
            
            # Evento 1 hora antes de la fecha objetivo
            start_time = reminder.target_datetime - timezone.timedelta(hours=1)
            end_time = reminder.target_datetime
            
            event = {
                'summary': subject,
                'description': f"""
{description}

Detalles:
• Título: {reminder.title}
• Usuario: {user_name}
• Creado: {reminder.created_at.strftime('%d/%m/%Y %H:%M')}
• Sistema: Planificador IA

Gestionar: {settings.SITE_URL}/reminders/
                """.strip(),
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Guayaquil',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Guayaquil',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 30},
                        {'method': 'popup', 'minutes': 15},
                    ],
                },
                'attendees': [
                    {'email': reminder.user.email}
                ]
            }
            
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            return created_event.get('id'), created_event.get('htmlLink')
            
        except Exception as e:
            print(f"ERROR: Error al crear evento en Calendar: {str(e)}")
            logger.error(f"Calendar event creation failed: {e}")
            return None, None
    
    def _generate_email_content(self, reminder, user_name, ai_subject=None, ai_description=None, calendar_link=None):
        """Genera contenido del email"""
        
        # Generar asunto inteligente
        if ai_subject:
            subject = ai_subject
        else:
            time_until = reminder.target_datetime - timezone.now()
            if time_until.total_seconds() < 3600:
                urgency = "URGENTE"
            elif time_until.total_seconds() < 86400:
                urgency = "PRÓXIMO"
            else:
                urgency = "RECORDATORIO"
            subject = f"{urgency}: {reminder.title}"
        
        # Generar mensaje de IA
        if ai_description:
            ai_message = ai_description
        else:
            ai_message = self._generate_smart_message(reminder, user_name)
        
        # Contexto para template
        context = {
            'user_name': user_name,
            'user_email': reminder.user.email,
            'reminder': reminder,
            'ai_subject': subject,
            'ai_message': ai_message,
            'calendar_link': calendar_link,  # Agregar link de calendario
            'site_url': settings.SITE_URL,
            'unsubscribe_url': f"{settings.SITE_URL}/reminders/unsubscribe/{reminder.user.id}/",
            'respond_urls': {
                'completed': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/completed/",
                'snooze': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/snooze/",
                'cancel': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/cancel/",
            }
        }
        
        # Renderizar template
        try:
            html_content = render_to_string('reminder_email.html', context)
            print("SUCCESS: Template renderizado correctamente")
        except Exception as e:
            print(f"WARNING: Error al renderizar template: {e}")
            # Template de respaldo HTML simple
            html_content = self._get_fallback_template(context, reminder, user_name, ai_message, calendar_link)
        
        return {
            'subject': subject,
            'html': html_content
        }
    
    def _generate_smart_message(self, reminder, user_name):
        """Genera mensaje inteligente"""
        time_until = reminder.target_datetime - timezone.now()
        
        if time_until.total_seconds() < 3600:
            time_context = "¡Es hora de comenzar!"
            advice = "Tienes todo listo, solo falta dar el primer paso."
        elif time_until.total_seconds() < 7200:
            time_context = "Faltan aproximadamente 2 horas"
            advice = "Es un buen momento para hacer los preparativos finales."
        elif time_until.days == 1:
            time_context = "¡Mañana es el gran día!"
            advice = "Revisa tu material y asegúrate de tener todo organizado."
        else:
            days = time_until.days
            time_context = f"Faltan {days} días"
            advice = "Aún tienes tiempo para planificar y prepararte bien."
        
        return f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin: 20px 0;">
            <h3 style="margin: 0 0 10px 0;">Mensaje de tu Asistente IA</h3>
            <p style="margin: 0;"><strong>{time_context}</strong></p>
            <p style="margin: 10px 0 0 0;">{advice}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <p style="margin: 0;"><strong>Consejo personalizado para {user_name}:</strong></p>
            <p style="margin: 5px 0 0 0;">Recuerda mantener tu espacio de trabajo organizado y tomar descansos regulares para maximizar tu productividad.</p>
        </div>
        """
    
    def _get_fallback_template(self, context, reminder, user_name, ai_message, calendar_link=None):
        """Template de respaldo simple"""
        calendar_section = ""
        if calendar_link:
            calendar_section = f"""
            <div style="background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #28a745;">
                <h4 style="margin-top: 0; color: #2e7d32;">📅 Evento en Google Calendar</h4>
                <p style="margin: 10px 0;">Este recordatorio también se ha agregado a tu Google Calendar.</p>
                <a href="{calendar_link}" style="background: #4285f4; color: white; padding: 8px 16px; text-decoration: none; border-radius: 5px; display: inline-block;">
                    📅 Ver en Google Calendar
                </a>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Recordatorio - {reminder.title}</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px; margin-bottom: 20px; }}
                .btn {{ display: inline-block; padding: 12px 24px; margin: 5px; text-decoration: none; border-radius: 25px; color: white; font-weight: bold; }}
                .btn-success {{ background: #28a745; }}
                .btn-warning {{ background: #ffc107; color: #212529; }}
                .btn-secondary {{ background: #6c757d; }}
                .actions {{ text-align: center; margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recordatorio Inteligente</h1>
                    <p>Planificador IA - StudiFly</p>
                </div>
                
                <h2>{reminder.title}</h2>
                <p><strong>Hola {user_name},</strong></p>
                <p>Este es tu recordatorio para: <strong>{reminder.title}</strong></p>
                <p><strong>Fecha objetivo:</strong> {reminder.target_datetime.strftime('%d/%m/%Y %H:%M')}</p>
                
                {f'<p><strong>Descripción:</strong><br>{reminder.description}</p>' if reminder.description else ''}
                
                {ai_message}
                
                {calendar_section}
                
                <div class="actions">
                    <h3>¿Qué quieres hacer?</h3>
                    <a href="{context['respond_urls']['completed']}" class="btn btn-success">¡Ya lo completé!</a>
                    <a href="{context['respond_urls']['snooze']}" class="btn btn-warning">Recordar en 15 min</a>
                    <a href="{context['respond_urls']['cancel']}" class="btn btn-secondary">Cancelar recordatorio</a>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
                    <p>Email automático del Planificador IA</p>
                    <p><a href="{context['unsubscribe_url']}">Desuscribirse</a></p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_message(self, to_email, subject, html_content, reminder):
        """Crea mensaje de email para Gmail API - Anti-SPAM"""
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        
        # CAMBIO IMPORTANTE: Usar el mismo email como From para evitar SPAM
        message['from'] = to_email
        message['subject'] = subject
        
        # Headers mejorados para evitar SPAM
        message['X-Reminder-ID'] = str(reminder.id)
        message['X-Mailer'] = 'StudiFly-AI'
        message['X-Priority'] = '3'
        message['Message-ID'] = f"<{reminder.id}@studifly-ai.local>"
        message['Date'] = timezone.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Agregar texto plano para evitar filtros de spam
        text_content = f"""
Recordatorio: {reminder.title}

Hola {reminder.get_user_full_name()},

Este es tu recordatorio para: {reminder.title}
Fecha objetivo: {reminder.target_datetime.strftime('%d/%m/%Y %H:%M')}

{reminder.description if reminder.description else ''}

Acciones disponibles:
- Marcar como completado: {settings.SITE_URL}/reminders/respond/{reminder.id}/completed/
- Posponer 15 minutos: {settings.SITE_URL}/reminders/respond/{reminder.id}/snooze/
- Cancelar recordatorio: {settings.SITE_URL}/reminders/respond/{reminder.id}/cancel/

--
Planificador IA - StudiFly
Sistema automatico de recordatorios
        """.strip()
        
        # Adjuntar ambos formatos
        text_part = MIMEText(text_content, 'plain', 'utf-8')
        html_part = MIMEText(html_content, 'html', 'utf-8')
        
        message.attach(text_part)
        message.attach(html_part)
        
        # Codificar para Gmail API
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

# Instancia global con manejo de errores mejorado
try:
    gmail_service = GmailService()
    print("SUCCESS: Gmail Service inicializado correctamente")
except Exception as e:
    print(f"ERROR: Error al inicializar Gmail Service: {e}")
    gmail_service = None