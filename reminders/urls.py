from django.urls import path
from . import views

app_name = 'reminders'

urlpatterns = [
    # Vistas principales
    path('', views.reminder_list, name='list'),
    path('create/', views.create_reminder, name='create'),
    path('configuration/', views.reminder_configuration, name='configuration'),
    
    # API endpoints para respuestas de email (sin login requerido)
    path('respond/<uuid:reminder_id>/<str:action>/', views.respond_reminder, name='respond'),
    
    # AJAX endpoints (requieren login) - VERIFICAR QUE EXISTAN:
    path('ajax/test-send/<uuid:reminder_id>/', views.test_send_reminder, name='test_send'),
    path('ajax/toggle-status/<uuid:reminder_id>/', views.toggle_reminder_status, name='toggle_status'),
]