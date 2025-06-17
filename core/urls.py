# core/urls.py
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Páginas principales
    path('', views.home, name='home'),
    path('perfil/', views.perfil, name='perfil'),
    path('configuracion/', views.settings, name='settings'),
    
    # URLs para funcionalidad de avatar
    path('upload-avatar/', views.upload_avatar, name='upload_avatar'),
    path('remove-avatar/', views.remove_avatar, name='remove_avatar'),
    path('get-datetime/', views.get_current_datetime, name='get_datetime'),
    
    # URLs para establecimiento de contraseña (usuarios de Google)
    path('password/setup/', views.request_password_setup, name='request_password_setup'),
    path('password/verify/', views.verify_password_code, name='verify_password_code'),
    path('password/set/', views.set_password, name='set_password'),
    
    # Vista semanal y análisis
    path('weekly-view/', views.weekly_view, name='weekly_view'),
]