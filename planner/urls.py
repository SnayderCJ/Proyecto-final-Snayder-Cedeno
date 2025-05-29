from django.urls import path
from planner import views

app_name = "planner"

urlpatterns = [
   # Ruta Principal
   path('horarios/', views.calendar_view, name='horarios'),
   path('event/create/', views.event_create, name='event_create'),
   path('event/<int:pk>/edit/', views.event_edit, name='event_edit'),
   path('event/<int:pk>/delete/', views.event_delete, name='event_delete'),
   path('event/<int:pk>/', views.event_detail, name='event_detail'),
   
]