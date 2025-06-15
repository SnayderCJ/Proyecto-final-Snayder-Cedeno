# reminders/services/gmail_service.py
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
    """Servicio integrado con tu configuración Gmail existente"""
    
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/calendar'
    ]
    
    def __init__(self):
        self.gmail_service = None
        self.calendar_service = None
        self._authenticate()
    
    def _authenticate(self):
        """Usa tu configuración OAuth existente"""
        try:
            creds = None
            
            # Buscar token existente
            token_path = os.path.join(settings.BASE_DIR, 'token.json')
            credentials_path = os.path.join(settings.BASE_DIR, 'studiFly_desktop_client.json')
            
            if os.path.exists(token_path):
                creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if os.path.exists(credentials_path):
                        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, self.SCOPES)
                        creds = flow.run_local_server(port=0)
                    else:
                        raise FileNotFoundError("No se encontró el archivo de credenciales de Google")
                
                # Guardar credenciales
                with open(token_path, 'w') as token:
                    token.write(creds.to_json())
            
            # Crear servicios
            self.gmail_service = build('gmail', 'v1', credentials=creds)
            self.calendar_service = build('calendar', 'v3', credentials=creds)
            
            logger.info("Google services authenticated successfully")
            
        except Exception as e:
            logger.error(f"Google authentication failed: {str(e)}")
            raise
    
    def send_reminder_email_with_calendar(self, reminder, ai_subject=None, ai_description=None, create_calendar_event=True):
        """
        Envía recordatorio por email y opcionalmente crea evento en Google Calendar
        
        Args:
            reminder: Objeto Reminder
            ai_subject: Asunto generado por IA
            ai_description: Descripción generada por IA
            create_calendar_event: Si crear evento en Google Calendar
        """
        try:
            user = reminder.user
            
            # Verificar que el usuario tenga email (viene de tu OAuth)
            if not user.email:
                raise ValueError(f"Usuario {user.username} no tiene email configurado")
            
            # Usar datos de tu sistema OAuth existente
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
                calendar_event_id, calendar_link = self._create_calendar_event(
                    reminder, 
                    user_name, 
                    ai_subject, 
                    ai_description
                )
            
            # Agregar link del calendario al email si existe
            if calendar_link:
                email_content['calendar_link'] = calendar_link
            
            # Crear y enviar mensaje
            message = self._create_message(
                to_email=user.email,
                subject=email_content['subject'],
                html_content=email_content['html'],
                reminder=reminder
            )
            
            # Enviar email
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
            
            logger.info(f"Email sent successfully to {user.email} for reminder {reminder.id}")
            
            return {
                'success': True,
                'email_id': result.get('id', ''),
                'calendar_event_id': calendar_event_id,
                'calendar_link': calendar_link
            }
            
        except Exception as e:
            logger.error(f"Failed to send reminder {reminder.id}: {str(e)}")
            reminder.last_error = str(e)
            reminder.send_attempts += 1
            reminder.status = 'failed'
            reminder.save()
            return {'success': False, 'error': str(e)}
    
    def _create_calendar_event(self, reminder, user_name, ai_subject=None, ai_description=None):
        """Crea evento en Google Calendar"""
        try:
            # Preparar datos del evento
            subject = ai_subject or f"📅 {reminder.title}"
            description = ai_description or reminder.description or "Recordatorio creado automáticamente"
            
            # Crear evento una hora antes de la fecha objetivo
            start_time = reminder.target_datetime - timezone.timedelta(hours=1)
            end_time = reminder.target_datetime
            
            event = {
                'summary': subject,
                'description': f"""
{description}

📝 Detalles:
• Título: {reminder.title}
• Usuario: {user_name}
• Creado: {reminder.created_at.strftime('%d/%m/%Y %H:%M')}
• Sistema: Planificador IA

🔗 Gestionar recordatorio: {settings.SITE_URL}/reminders/
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
            
            # Crear evento
            created_event = self.calendar_service.events().insert(
                calendarId='primary',
                body=event
            ).execute()
            
            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            
            logger.info(f"Calendar event created: {event_id}")
            return event_id, event_link
            
        except Exception as e:
            logger.error(f"Failed to create calendar event: {str(e)}")
            return None, None
    
    def _generate_email_content(self, reminder, user_name, ai_subject=None, ai_description=None):
        """Genera contenido del email usando datos de tu OAuth"""
        
        # Usar asunto de IA o generar uno inteligente
        if ai_subject:
            subject = ai_subject
        else:
            time_until = reminder.target_datetime - timezone.now()
            if time_until.total_seconds() < 3600:
                urgency = "🚨 URGENTE"
            elif time_until.total_seconds() < 86400:
                urgency = "⏰ PRÓXIMO"
            else:
                urgency = "📅 RECORDATORIO"
            subject = f"{urgency}: {reminder.title}"
        
        # Usar descripción de IA o generar mensaje inteligente
        if ai_description:
            ai_message = ai_description
        else:
            ai_message = self._generate_smart_message(reminder, user_name)
        
        # Renderizar template (ajustado a tu estructura)
        context = {
            'user_name': user_name,
            'user_email': reminder.user.email,
            'reminder': reminder,
            'ai_subject': subject,
            'ai_message': ai_message,
            'site_url': settings.SITE_URL,
            'unsubscribe_url': f"{settings.SITE_URL}/reminders/unsubscribe/{reminder.user.id}/",
            'respond_urls': {
                'completed': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/completed/",
                'snooze': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/snooze/",
                'cancel': f"{settings.SITE_URL}/reminders/respond/{reminder.id}/cancel/",
            }
        }
        
        # RUTA AJUSTADA A TU ESTRUCTURA
        html_content = render_to_string('reminder_email.html', context)
        
        return {
            'subject': subject,
            'html': html_content
        }
    
    def _generate_smart_message(self, reminder, user_name):
        """Genera mensaje inteligente mientras desarrollas tu IA"""
        time_until = reminder.target_datetime - timezone.now()
        
        if time_until.total_seconds() < 3600:
            time_context = "¡Es hora de comenzar! ⏰"
            advice = "Tienes todo listo, solo falta dar el primer paso."
        elif time_until.total_seconds() < 7200:
            time_context = "Faltan aproximadamente 2 horas ⏳"
            advice = "Es un buen momento para hacer los preparativos finales."
        elif time_until.days == 1:
            time_context = "¡Mañana es el gran día! 🌅"
            advice = "Revisa tu material y asegúrate de tener todo organizado."
        else:
            days = time_until.days
            time_context = f"Faltan {days} días 📅"
            advice = "Aún tienes tiempo para planificar y prepararte bien."
        
        return f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 20px; border-radius: 10px; color: white; margin: 20px 0;">
            <h3 style="margin: 0 0 10px 0;">🤖 Mensaje de tu Asistente IA</h3>
            <p style="margin: 0;"><strong>{time_context}</strong></p>
            <p style="margin: 10px 0 0 0;">{advice}</p>
        </div>
        
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 15px 0;">
            <p style="margin: 0;"><strong>💡 Consejo personalizado:</strong></p>
            <p style="margin: 5px 0 0 0;">Recuerda mantener tu espacio de trabajo organizado y tomar descansos regulares para maximizar tu productividad.</p>
        </div>
        """
    
    def _create_message(self, to_email, subject, html_content, reminder):
        """Crea mensaje de email con tu configuración"""
        message = MIMEMultipart('alternative')
        message['to'] = to_email
        message['from'] = settings.DEFAULT_FROM_EMAIL
        message['subject'] = subject
        
        # Headers personalizados
        message['X-Reminder-ID'] = str(reminder.id)
        message['X-Mailer'] = 'Planificador IA'
        
        # Contenido HTML
        html_part = MIMEText(html_content, 'html', 'utf-8')
        message.attach(html_part)
        
        # Codificar
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        return {'raw': raw_message}

# Instancia global
gmail_service = GmailService()