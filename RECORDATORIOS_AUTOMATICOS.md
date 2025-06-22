# Sistema de Recordatorios Automáticos 🔔

Este sistema permite enviar recordatorios automáticos por email y crear eventos en Google Calendar para las tareas programadas.

## Configuración Inicial 🚀

1. Asegúrate de tener las siguientes apps instaladas en `settings.py`:
   - ✅ App `reminders` en `INSTALLED_APPS`

2. Ejecuta las migraciones:
```bash
python manage.py makemigrations reminders
python manage.py migrate
```

3. Configura los scripts de recordatorios automáticos:

### Linux/Mac
```bash
chmod +x setup_reminder_crons.sh
./setup_reminder_crons.sh
```

### Windows
```cmd
setup_reminder_scheduler_windows.bat
```

## Comandos Disponibles 🛠️

### Enviar recordatorios que están programados
```bash
python manage.py send_pending_reminders

# Modo simulación (no envía realmente)
python manage.py send_pending_reminders --dry-run
```

### Limpiar recordatorios antiguos
```bash
# Limpiar recordatorios completados de más de 30 días
python manage.py cleanup_reminders

# Personalizar días de antigüedad
python manage.py cleanup_reminders --days 15 --log-days 60

# Modo simulación
python manage.py cleanup_reminders --dry-run
```

### Probar sistema completo
```bash
# Probar con un usuario específico
python manage.py test_reminder_system --user [username]

# Probar sin envío de emails
python manage.py test_reminder_system --user [username] --skip-email
```

## Configuración de Usuario 👤

Cada usuario puede configurar sus recordatorios en `/reminders/configuration/`:

- Activar/desactivar recordatorios
- Elegir tipo de recordatorio (email, calendario o ambos)
- Configurar frecuencia y timing
- Personalizar preferencias de notificación

## Archivos de Log 📝

Los logs se guardan en:
- `logs/reminders.log`: Envío de recordatorios
- `logs/cleanup.log`: Limpieza automática

### Ver logs en tiempo real:

#### Linux/Mac
```bash
tail -f logs/reminders.log
```

#### Windows
```powershell
Get-Content logs\reminders.log -Wait
```

## Verificar Configuración ✅

### Linux/Mac
```bash
crontab -l | grep reminders
```

### Windows
```cmd
schtasks /query /tn "PlanificadorIA_*"
```

## Solución de Problemas 🔧

1. Si los recordatorios no se envían:
   - Verifica los logs en `logs/reminders.log`
   - Asegúrate que el servicio de email esté configurado
   - Revisa las credenciales en `.env`

2. Para limpiar todos los recordatorios antiguos:
```bash
python manage.py cleanup_reminders --days 0 --dry-run
```

3. Si necesitas reiniciar el servicio:
   - Linux/Mac: Ejecuta `setup_reminder_crons.sh`
   - Windows: Ejecuta `setup_reminder_scheduler_windows.bat`

## Estructura de Archivos 📁

```
reminders/
├── management/
│   └── commands/
│       ├── send_pending_reminders.py
│       ├── cleanup_reminders.py
│       └── test_reminder_system.py
├── services/
│   └── gmail_service.py
├── templates/
│   └── emails/
│       ├── reminder_email.html
│       └── reminder_email.txt
└── models.py
```

## Mantenimiento 🔄

### Mensual: Limpiar datos antiguos
```bash
python manage.py cleanup_reminders --days 30
```

### Configuración de Cron/Scheduler
#### Linux/Mac
```bash
./setup_reminder_crons.sh
```

#### Windows
```cmd
setup_reminder_scheduler_windows.bat
