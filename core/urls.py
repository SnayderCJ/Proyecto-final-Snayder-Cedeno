# core/urls.py
from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
    # Rutas principales
    path('', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('settings/', views.settings, name='settings'),
    
    # Rutas para establecimiento de contraseña
    path('password/setup/request/', views.request_password_setup, name='request_password_setup'),
    path('password/setup/verify/', views.verify_password_code, name='verify_password_code'),
    path('password/setup/set/', views.set_password, name='set_password'),
]