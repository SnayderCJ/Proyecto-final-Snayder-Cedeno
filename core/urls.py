# core/urls.py
from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
   # Ruta Principal
   path('', views.home, name='home'),
   path('perfil/', views.perfil, name='perfil'),
   path('settings/', views.settings, name='settings'),
]