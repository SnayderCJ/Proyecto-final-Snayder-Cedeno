@echo off
setlocal enabledelayedexpansion

echo.
echo 🔄 Configurando tareas programadas para recordatorios automaticos...
echo.

:: Obtener el directorio actual del proyecto
set PROJECT_DIR=%cd%
set PYTHON_PATH=python

:: Verificar si existe un virtualenv
if exist "%PROJECT_DIR%\venv\Scripts\python.exe" (
    set PYTHON_PATH=%PROJECT_DIR%\venv\Scripts\python.exe
    echo ✅ Usando Python del virtualenv: !PYTHON_PATH!
) else (
    echo ⚠️ No se encontro virtualenv, usando Python del sistema
)

:: Crear directorio de logs si no existe
if not exist "%PROJECT_DIR%\logs" (
    mkdir "%PROJECT_DIR%\logs"
    echo ✅ Directorio de logs creado
)

:: Verificar que los comandos existen
echo.
echo 🔍 Verificando comandos...

"!PYTHON_PATH!" manage.py send_pending_reminders --help >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Comando send_pending_reminders disponible
) else (
    echo ❌ Error: Comando send_pending_reminders no encontrado
    pause
    exit /b 1
)

"!PYTHON_PATH!" manage.py cleanup_reminders --help >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ Comando cleanup_reminders disponible
) else (
    echo ❌ Error: Comando cleanup_reminders no encontrado
    pause
    exit /b 1
)

:: Eliminar tareas anteriores si existen
echo.
echo 🗑️ Eliminando tareas anteriores...
schtasks /delete /tn "StudyFly_SendReminders" /f >nul 2>&1
schtasks /delete /tn "StudyFly_CleanupReminders" /f >nul 2>&1
schtasks /delete /tn "StudyFly_SyncPlannerEvents" /f >nul 2>&1

:: Crear tarea para envío de recordatorios (cada 5 minutos)
echo.
echo 📝 Creando tarea de envío de recordatorios...
schtasks /create /tn "StudyFly_SendReminders" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && \"%PYTHON_PATH%\" manage.py send_pending_reminders >> logs\reminders.log 2>&1" /sc minute /mo 5 /ru "SYSTEM" /f

if !errorlevel! equ 0 (
    echo ✅ Tarea de envío creada exitosamente
) else (
    echo ❌ Error al crear tarea de envío
    pause
    exit /b 1
)

:: Crear tarea para limpieza (diariamente a las 4 AM)
echo.
echo 🧹 Creando tarea de limpieza...
schtasks /create /tn "StudyFly_CleanupReminders" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && \"%PYTHON_PATH%\" manage.py cleanup_reminders --days 30 >> logs\cleanup.log 2>&1" /sc daily /st 04:00 /ru "SYSTEM" /f

if !errorlevel! equ 0 (
    echo ✅ Tarea de limpieza creada exitosamente
) else (
    echo ❌ Error al crear tarea de limpieza
    pause
    exit /b 1
)

:: Crear tarea para sincronización con planner (diariamente a las 6 AM)
echo.
echo 🔄 Creando tarea de sincronización...
schtasks /create /tn "StudyFly_SyncPlannerEvents" /tr "cmd /c cd /d \"%PROJECT_DIR%\" && \"%PYTHON_PATH%\" manage.py sync_planner_events --days-ahead 7 >> logs\sync.log 2>&1" /sc daily /st 06:00 /ru "SYSTEM" /f

if !errorlevel! equ 0 (
    echo ✅ Tarea de sincronización creada exitosamente
) else (
    echo ❌ Error al crear tarea de sincronización
    pause
    exit /b 1
)

:: Mostrar resumen
echo.
echo 📊 Resumen de configuración:
echo 📁 Directorio del proyecto: %PROJECT_DIR%
echo 🐍 Python: !PYTHON_PATH!
echo 📝 Logs en: %PROJECT_DIR%\logs\
echo.
echo 📋 Tareas programadas creadas:
echo ➜ StudyFly_SendReminders: Cada 5 minutos
echo ➜ StudyFly_CleanupReminders: Diariamente a las 4:00 AM
echo ➜ StudyFly_SyncPlannerEvents: Diariamente a las 6:00 AM
echo.

:: Verificar tareas creadas
echo 🔍 Verificando tareas creadas...
schtasks /query /tn "StudyFly_SendReminders" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ StudyFly_SendReminders: Activa
) else (
    echo ❌ StudyFly_SendReminders: No encontrada
)

schtasks /query /tn "StudyFly_CleanupReminders" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ StudyFly_CleanupReminders: Activa
) else (
    echo ❌ StudyFly_CleanupReminders: No encontrada
)

schtasks /query /tn "StudyFly_SyncPlannerEvents" >nul 2>&1
if !errorlevel! equ 0 (
    echo ✅ StudyFly_SyncPlannerEvents: Activa
) else (
    echo ❌ StudyFly_SyncPlannerEvents: No encontrada
)

echo.
echo ✨ Configuración completada
echo 💡 Tip: Revisa los logs en logs\reminders.log, logs\cleanup.log y logs\sync.log
echo 💡 Para ver las tareas: Ejecuta "taskschd.msc" o "schtasks /query /fo table"
echo 💡 Para eliminar las tareas: Ejecuta "remove_reminder_scheduler_windows.bat"
echo.

:: Crear script de eliminación
echo @echo off > remove_reminder_scheduler_windows.bat
echo echo Eliminando tareas programadas de StudyFly... >> remove_reminder_scheduler_windows.bat
echo schtasks /delete /tn "StudyFly_SendReminders" /f >> remove_reminder_scheduler_windows.bat
echo schtasks /delete /tn "StudyFly_CleanupReminders" /f >> remove_reminder_scheduler_windows.bat
echo schtasks /delete /tn "StudyFly_SyncPlannerEvents" /f >> remove_reminder_scheduler_windows.bat
echo echo ✅ Tareas eliminadas >> remove_reminder_scheduler_windows.bat
echo pause >> remove_reminder_scheduler_windows.bat

echo ✅ Script de eliminación creado: remove_reminder_scheduler_windows.bat
echo.
pause
