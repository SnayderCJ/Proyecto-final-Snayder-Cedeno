# Documentación del Sistema de IA para Optimización de Horarios

## Estructura del Sistema

### 1. Archivos Principales
- `ai_optimizer.py`: Clase principal que maneja la IA
- `trained_models/`: Carpeta con los archivos del modelo
  - `smart_scheduler_model.joblib` (937KB): Modelo principal de machine learning
  - `smart_scheduler_encoders.joblib` (1KB): Codificadores para convertir datos
  - `smart_scheduler_scaler.joblib` (1KB): Normaliza los datos numéricos
  - `smart_scheduler_metadata.json` (1KB): Info del modelo y configuraciones

### 2. Cómo Funciona la IA

#### Inicialización
```python
# Se carga automáticamente al iniciar
optimizer = SmartScheduleOptimizer()
# Carga los archivos .joblib y el JSON
```

#### Proceso de Optimización
```python
# Cuando el usuario da click en "Optimizar"
@login_required
def optimize_schedule(request):
    optimizer = SmartScheduleOptimizer()
    # Agarra los eventos del usuario
    user_events = Event.objects.filter(user=request.user)
    # La IA analiza y sugiere mejores horarios
    suggestions = optimizer.optimize_schedule(user_events, start_date, end_date)
```

### 3. Datos que Usa
- Tipo de evento (tarea, clase, examen, etc.)
- Prioridad (alta, media, baja)
- Hora del día (0-23)
- Día de la semana (0-6)
- Fecha límite

### 4. Cómo Hace las Predicciones
1. Agarra un evento
2. Prueba todas las horas posibles (6:00 - 22:00)
3. Para cada hora calcula:
   - Probabilidad base del modelo
   - Ajustes por tipo de evento
   - Ajustes por prioridad
   - Ajustes por deadline
4. Escoge la mejor hora

### 5. Archivos del Modelo
- **model.joblib**: El modelo entrenado de Gradient Boosting
- **encoders.joblib**: Convierte texto a números (ej: "alta" → 2)
- **scaler.joblib**: Normaliza números (ej: hora 23 → 0.95)
- **metadata.json**: Guarda info como:
  ```json
  {
    "version": "2.0",
    "trained_date": "2025-06-17",
    "event_types": ["tarea", "clase"...],
    "priorities": ["alta", "media", "baja"]
  }
  ```

### 6. Endpoints
- `/planner/optimize/`: 
  - POST: Recibe eventos y devuelve sugerencias
  - Formato respuesta:
    ```json
    {
      "success": true,
      "suggestions": [
        {
          "event_id": 1,
          "current_time": "2025-06-17T08:00:00",
          "suggested_time": "2025-06-17T09:00:00",
          "improvement_score": 117.3,
          "reason": "Mejor hora para concentración"
        }
      ]
    }
    ```

### 7. Importante Saber
- No se reentrena automáticamente
- Los archivos .joblib son binarios, no los edites
- El JSON sí se puede editar si necesitas cambiar configuraciones
- Siempre revisa que los 4 archivos estén en trained_models/

### 8. Si Algo Falla
1. Revisa que existan los 4 archivos
2. Checa los logs por errores
3. Verifica que los tipos de eventos coincidan con el JSON
4. Reinicia el servidor Django

### 9. Para Mejorar el Sistema
- Podrías agregar reentrenamiento automático
- Implementar feedback de usuarios
- Añadir más tipos de eventos en metadata.json
- Mejorar las razones de sugerencias

Cualquier duda me avisas! 👍
