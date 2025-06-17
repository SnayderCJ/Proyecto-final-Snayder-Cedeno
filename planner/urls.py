from django.urls import path
from planner import views
from . import views
from .views import (
    calendar_view, event_create, event_edit, event_delete, event_detail,
     focused_time_view  # ✅ asegurado aquí
)
app_name = "planner"

urlpatterns = [
   # Ruta Principal
   path('horarios/', views.calendar_view, name='horarios'),
   path('event/create/', views.event_create, name='event_create'),
   path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
   path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
   path('event/<int:pk>/', views.event_detail, name='event_detail'),
   path('tiempo-enfocado/', focused_time_view, name='focused_time'),
   path("productividad/", views.productividad_view, name="productividad"),
   path('registrar-bloque-temporizador/', views.registrar_bloque_temporizador, name='registrar_bloque_temporizador'),
   path('api/productividad/', views.obtener_estadisticas_productividad, name='api_productividad'),
   path("api/productividad/", views.productividad_api, name="productividad_api"),
]