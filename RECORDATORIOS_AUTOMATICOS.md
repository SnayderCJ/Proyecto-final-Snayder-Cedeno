# 🔔 Sistema de Recordatorios Automáticos

## 📋 Descripción General

Este sistema permite enviar recordatorios automáticos por email y Google Calendar basados en los eventos de tu planificador. Los recordatorios se envían automáticamente según la configuración de cada usuario.

## 🚀 Configuración Inicial

### 1. Verificar Requisitos

Asegúrate de tener configurado:
- ✅ Gmail API (archivos `studiFly_desktop_client.json` y `token.json`)
- ✅ Google Calendar API
- ✅ App `reminders` en `INSTALLED_APPS`

### 2. Ejecutar Migraciones

```bash
python manage.py makemigrations reminders
python manage.py migrate
```

### 3. Configurar Tareas Automáticas

#### Para Linux/Mac (Cronjobs):
```bash
chmod +x setup_reminder_crons.sh
./setup_reminder_crons.sh
```

#### Para Windows (Programador de Tareas):
```cmd
setup_reminder_scheduler_windows.bat
```

## 🛠️ Comandos Disponibles

### 1. Enviar Recordatorios Pendientes
```bash
# Enviar recordatorios que están programados
python manage.py send_pending_reminders

# Modo simulación (no envía realmente)
python manage.py send_pending_reminders --dry-run
```

### 2. Limpiar Recordatorios Antiguos
```bash
# Limpiar recordatorios completados de más de 30 días
python manage.py cleanup_reminders

# Personalizar días de antigüedad
python manage.py cleanup_reminders --days 15 --log-days 60

# Modo simulación
python manage.py cleanup_reminders --dry-run
```

### 3. Sincronizar con Eventos del Planner
```bash
# Crear recordatorios automáticos para eventos futuros
python manage.py sync_planner_events

# Solo para un usuario específico
python manage.py sync_planner_events --user username

# Personalizar días hacia adelante
python manage.py sync_planner_events --days-ahead 14

# Modo simulación
python manage.py sync_planner_events --dry-run
```

### 4. Diagnóstico del Sistema
```bash
# Verificar configuración completa
python manage.py test_gmail

# Enviar email de prueba
python manage.py test_gmail --send-test --user username
```

## ⚙️ Configuración de Usuario

Cada usuario puede configurar sus recordatorios en `/reminders/configuration/`:

### Opciones Disponibles:
- **Recordatorios activos**: Habilitar/deshabilitar completamente
- **Tipo preferido**: Solo email, solo calendar, o ambos
- **Tiempo de anticipación**: 15 min, 1 hora, 1 día, etc.
- **Frecuencia adaptativa**: Reduce automáticamente si ignoras recordatorios

### Frecuencia Adaptativa:
- **Alta**: Todos los recordatorios se envían
- **Media**: No se envían recordatorios inmediatos
- **Baja**: Solo recordatorios de 1+ días
- **Deshabilitado**: No se envían recordatorios

## 📅 Programación Automática

### Tareas Configuradas:

1. **Envío de Recordatorios**: Cada 5 minutos
   - Busca recordatorios pendientes
   - Envía emails y crea eventos de calendario
   - Respeta la configuración de cada usuario

2. **Limpieza**: Diariamente a las 4:00 AM
   - Marca recordatorios vencidos como fallidos
   - Elimina recordatorios completados antiguos
   - Limpia logs antiguos

3. **Sincronización**: Diariamente a las 6:00 AM
   - Crea recordatorios para eventos futuros del planner
   - Solo para eventos que no tienen recordatorio

## 📊 Monitoreo y Logs

### Archivos de Log:
- `logs/reminders.log`: Envío de recordatorios
- `logs/cleanup.log`: Limpieza automática
- `logs/sync.log`: Sincronización con planner

### Ver Logs en Tiempo Real:
```bash
# Linux/Mac
tail -f logs/reminders.log

# Windows
Get-Content logs\reminders.log -Wait
```

### Verificar Tareas Programadas:

#### Linux/Mac:
```bash
crontab -l | grep reminders
```

#### Windows:
```cmd
schtasks /query /fo table | findstr StudyFly
```

## 🔧 Solución de Problemas

### Problema: No se envían recordatorios

1. **Verificar configuración OAuth**:
   ```bash
   python manage.py test_gmail
   ```

2. **Verificar tareas programadas**:
   ```bash
   # Linux/Mac
   crontab -l
   
   # Windows
   schtasks /query /tn "StudyFly_SendReminders"
   ```

3. **Revisar logs**:
   ```bash
   tail -20 logs/reminders.log
   ```

### Problema: Errores de autenticación

1. **Eliminar token y reautenticar**:
   ```bash
   rm token.json
   python manage.py test_gmail --send-test --user tu_usuario
   ```

2. **Verificar scopes en token.json**:
   - `https://www.googleapis.com/auth/gmail.send`
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/calendar`

### Problema: Recordatorios duplicados

1. **Limpiar recordatorios existentes**:
   ```bash
   python manage.py cleanup_reminders --days 0 --dry-run
   ```

2. **Verificar sincronización**:
   ```bash
   python manage.py sync_planner_events --dry-run
   ```

## 🎯 Funcionalidades Avanzadas

### 1. Respuesta desde Email
Los usuarios pueden responder a recordatorios directamente desde el email:
- **Completar**: Marca el recordatorio como completado
- **Posponer**: Retrasa el recordatorio 15 minutos
- **Cancelar**: Cancela el recordatorio

### 2. Frecuencia Adaptativa
El sistema aprende del comportamiento del usuario:
- Si ignoras 3+ recordatorios consecutivos, reduce la frecuencia
- Si respondes, resetea el contador

### 3. Integración con Planner
- Crea recordatorios automáticamente para eventos futuros
- Genera descripciones inteligentes según el tipo de evento
- Incluye consejos específicos (exámenes, tareas, etc.)

## 📱 Uso desde la Interfaz Web

### Crear Recordatorio Manual:
1. Ve a `/reminders/create/`
2. Llena el formulario
3. Opcionalmente envía una prueba inmediata

### Ver Recordatorios:
1. Ve a `/reminders/`
2. Filtra por estado
3. Usa acciones rápidas (enviar prueba, cambiar estado)

### Configurar Preferencias:
1. Ve a `/reminders/configuration/`
2. Ajusta tus preferencias
3. Ve estadísticas y logs recientes

## 🔄 Mantenimiento

### Comandos de Mantenimiento Regulares:

```bash
# Semanal: Verificar estado del sistema
python manage.py test_gmail

# Mensual: Limpiar datos antiguos
python manage.py cleanup_reminders --days 30

# Según necesidad: Re-sincronizar eventos
python manage.py sync_planner_events
```

### Actualizar Configuración de Tareas:

```bash
# Linux/Mac
./setup_reminder_crons.sh

# Windows
setup_reminder_scheduler_windows.bat
```

## 📞 Soporte

Si tienes problemas:

1. **Revisa los logs** en `logs/`
2. **Ejecuta diagnóstico**: `python manage.py test_gmail`
3. **Verifica configuración OAuth** en Google Cloud Console
4. **Consulta la documentación** de Django y Google APIs

---

¡Tu sistema de recordatorios automáticos está listo! 🎉
