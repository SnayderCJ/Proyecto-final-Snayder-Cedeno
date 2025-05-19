from django.urls import path
from core import views

app_name = "core"

urlpatterns = [
   # Ruta Principal
   path('', views.home, name='home'),
]