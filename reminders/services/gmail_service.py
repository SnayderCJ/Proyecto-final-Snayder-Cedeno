from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger("reminders")


class GmailService:
    """Servicio para enviar emails usando Gmail"""

    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL

    def send_reminder_email_with_calendar(
        self, reminder, ai_subject=None, ai_description=None
    ):
        """Envía un email de recordatorio con opción de calendario"""
        try:
            context = {
                "reminder": reminder,
                "user": reminder.user,
                "ai_description": ai_description or reminder.ai_description,
                "action_url": f"{settings.SITE_URL}/reminders/respond/{reminder.id}",
            }

            # Renderizar templates
            html_content = render_to_string("emails/reminder_email.html", context)
            text_content = strip_tags(html_content)

            # Crear mensaje
            subject = ai_subject or f"🔔 Recordatorio: {reminder.title}"
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[reminder.user.email],
                reply_to=[self.from_email],
            )

            # Agregar versión HTML
            email.attach_alternative(html_content, "text/html")

            # Enviar email
            email.send()

            # Registrar éxito
            logger.info(f"Recordatorio enviado exitosamente a {reminder.user.email}")
            return {"success": True}

        except Exception as e:
            # Registrar error
            error_msg = f"Error enviando recordatorio: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def send_test_email(self, user):
        """Envía un email de prueba para verificar la configuración"""
        try:
            context = {
                "user": user,
                "test_message": "¡Esta es una prueba del sistema de recordatorios!",
            }

            # Renderizar templates
            html_content = render_to_string("emails/test_email.html", context)
            text_content = strip_tags(html_content)

            # Crear mensaje
            email = EmailMultiAlternatives(
                subject="🧪 Prueba del Sistema de Recordatorios",
                body=text_content,
                from_email=self.from_email,
                to=[user.email],
                reply_to=[self.from_email],
            )

            # Agregar versión HTML
            email.attach_alternative(html_content, "text/html")

            # Enviar email
            email.send()

            # Registrar éxito
            logger.info(f"Email de prueba enviado exitosamente a {user.email}")
            return {"success": True}

        except Exception as e:
            # Registrar error
            error_msg = f"Error enviando email de prueba: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
