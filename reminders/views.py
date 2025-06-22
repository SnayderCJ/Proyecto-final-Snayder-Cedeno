from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
from .models import Reminder, ReminderConfig
from .services.gmail_service import GmailService


@login_required
def respond_to_reminder(request, reminder_id, action):
    """Vista para responder a un recordatorio desde el email"""
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)

    if action == "completed":
        reminder.mark_as_completed()
        messages.success(request, "¡Recordatorio marcado como completado!")

    elif action == "snooze":
        reminder.snooze(minutes=15)
        messages.info(request, "Recordatorio pospuesto 15 minutos")

    elif action == "cancel":
        reminder.cancel()
        messages.warning(request, "Recordatorio cancelado")

    return redirect("planner:home")


@login_required
def reminder_configuration(request):
    """Vista para configurar preferencias de recordatorios"""
    config, created = ReminderConfig.objects.get_or_create(user=request.user)

    if request.method == "POST":
        config.reminders_enabled = request.POST.get("reminders_enabled") == "on"
        config.email_enabled = request.POST.get("email_enabled") == "on"
        config.calendar_enabled = request.POST.get("calendar_enabled") == "on"
        config.preferred_type = request.POST.get("preferred_type", "email")
        config.current_frequency = request.POST.get("current_frequency", "normal")
        config.save()

        messages.success(request, "¡Preferencias de recordatorios actualizadas!")
        return redirect("reminders:configuration")

    context = {
        "config": config,
        "reminder_types": ReminderConfig.REMINDER_TYPES,
        "frequency_choices": ReminderConfig.FREQUENCY_CHOICES,
    }

    return render(request, "reminders/configuration.html", context)


@login_required
def test_reminder_service(request):
    """Vista para probar el servicio de recordatorios"""
    if not request.user.is_staff:
        messages.error(request, "No tienes permiso para acceder a esta función")
        return redirect("planner:home")

    try:
        # Crear recordatorio de prueba
        reminder = Reminder.objects.create(
            user=request.user,
            title="🧪 Recordatorio de Prueba",
            description="Este es un recordatorio de prueba.",
            target_datetime=timezone.now() + timezone.timedelta(minutes=5),
            reminder_type="both",
        )

        # Probar envío
        gmail_service = GmailService()
        result = gmail_service.send_reminder_email_with_calendar(
            reminder=reminder,
            ai_subject="🧪 PRUEBA - Sistema de Recordatorios",
            ai_description="<p>Este es un recordatorio de prueba del sistema.</p>",
        )

        if result.get("success"):
            messages.success(request, "¡Prueba exitosa! Revisa tu email.")
        else:
            messages.error(request, f"Error en la prueba: {result.get('error')}")

    except Exception as e:
        messages.error(request, f"Error inesperado: {str(e)}")

    return redirect("reminders:configuration")
