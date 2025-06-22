from django.urls import path
from . import views

app_name = "reminders"

urlpatterns = [
    path(
        "respond/<int:reminder_id>/<str:action>/",
        views.respond_to_reminder,
        name="respond",
    ),
    path("configuration/", views.reminder_configuration, name="configuration"),
    path("test/", views.test_reminder_service, name="test"),
]
