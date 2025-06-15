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
   path('event/<int:pk>/toggle-completion/', views.toggle_event_completion, name='toggle_event_completion'),
   
   # Optimizador de IA
   path('optimize-schedule/', views.optimize_schedule, name='optimize_schedule'),
   path('event/<int:pk>/update-ajax/', views.event_update_ajax, name='event_update_ajax'),
   path('list-user-events/', views.list_user_events, name='list_user_events'),
   
   # Tareas
   path('tareas/', views.tareas_view, name='tareas')
]
