@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   CONFIGURACION DE RECORDATORIOS
echo   Sistema de Planificador IA
echo ========================================
echo.

:: Obtener directorio actual
set PROJECT_DIR=%cd%
set PYTHON_CMD=python

:: Verificar que Python está disponible
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no encontrado en el PATH
    echo Por favor instala Python o agregalo al PATH
    pause
    exit /b 1
)

:: Verificar que los comandos de Django existen
%PYTHON_CMD% manage.py send_pending_reminders --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: Comando send_pending_reminders no encontrado
    echo Verifica que la app reminders este instalada
    pause
    exit /b 1
)

%PYTHON_CMD% manage.py cleanup_reminders --help >nul 2>&1
if errorlevel 1 (
    echo ERROR: Comando cleanup_reminders no encontrado
    echo Verifica que la app reminders este instalada
    pause
    exit /b 1
)

:: Crear directorio de logs si no existe
if not exist "logs" mkdir logs
if not exist "logs\reminders.log" echo. > logs\reminders.log
if not exist "logs\cleanup.log" echo. > logs\cleanup.log

echo ✅ Comandos verificados correctamente
echo.

:: Crear archivo de tarea programada XML
set TASK_XML=%TEMP%\reminder_task.xml

echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%TASK_XML%"
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%TASK_XML%"
echo   ^<RegistrationInfo^> >> "%TASK_XML%"
echo     ^<Description^>Envio automatico de recordatorios - Planificador IA^</Description^> >> "%TASK_XML%"
echo   ^</RegistrationInfo^> >> "%TASK_XML%"
echo   ^<Triggers^> >> "%TASK_XML%"
echo     ^<CalendarTrigger^> >> "%TASK_XML%"
echo       ^<Repetition^> >> "%TASK_XML%"
echo         ^<Interval^>PT5M^</Interval^> >> "%TASK_XML%"
echo       ^</Repetition^> >> "%TASK_XML%"
echo       ^<StartBoundary^>2024-01-01T00:00:00^</StartBoundary^> >> "%TASK_XML%"
echo       ^<Enabled^>true^</Enabled^> >> "%TASK_XML%"
echo       ^<ScheduleByDay^> >> "%TASK_XML%"
echo         ^<DaysInterval^>1^</DaysInterval^> >> "%TASK_XML%"
echo       ^</ScheduleByDay^> >> "%TASK_XML%"
echo     ^</CalendarTrigger^> >> "%TASK_XML%"
echo   ^</Triggers^> >> "%TASK_XML%"
echo   ^<Principals^> >> "%TASK_XML%"
echo     ^<Principal id="Author"^> >> "%TASK_XML%"
echo       ^<LogonType^>InteractiveToken^</LogonType^> >> "%TASK_XML%"
echo       ^<RunLevel^>LeastPrivilege^</RunLevel^> >> "%TASK_XML%"
echo     ^</Principal^> >> "%TASK_XML%"
echo   ^</Principals^> >> "%TASK_XML%"
echo   ^<Settings^> >> "%TASK_XML%"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%TASK_XML%"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%TASK_XML%"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%TASK_XML%"
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^> >> "%TASK_XML%"
echo     ^<StartWhenAvailable^>false^</StartWhenAvailable^> >> "%TASK_XML%"
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> "%TASK_XML%"
echo     ^<IdleSettings^> >> "%TASK_XML%"
echo       ^<StopOnIdleEnd^>true^</StopOnIdleEnd^> >> "%TASK_XML%"
echo       ^<RestartOnIdle^>false^</RestartOnIdle^> >> "%TASK_XML%"
echo     ^</IdleSettings^> >> "%TASK_XML%"
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> "%TASK_XML%"
echo     ^<Enabled^>true^</Enabled^> >> "%TASK_XML%"
echo     ^<Hidden^>false^</Hidden^> >> "%TASK_XML%"
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> "%TASK_XML%"
echo     ^<WakeToRun^>false^</WakeToRun^> >> "%TASK_XML%"
echo     ^<ExecutionTimeLimit^>PT1H^</ExecutionTimeLimit^> >> "%TASK_XML%"
echo     ^<Priority^>7^</Priority^> >> "%TASK_XML%"
echo   ^</Settings^> >> "%TASK_XML%"
echo   ^<Actions Context="Author"^> >> "%TASK_XML%"
echo     ^<Exec^> >> "%TASK_XML%"
echo       ^<Command^>cmd^</Command^> >> "%TASK_XML%"
echo       ^<Arguments^>/c "cd /d "%PROJECT_DIR%" && %PYTHON_CMD% manage.py send_pending_reminders >> logs\reminders.log 2>&1"^</Arguments^> >> "%TASK_XML%"
echo     ^</Exec^> >> "%TASK_XML%"
echo   ^</Actions^> >> "%TASK_XML%"
echo ^</Task^> >> "%TASK_XML%"

:: Crear tarea programada para limpieza
set CLEANUP_XML=%TEMP%\cleanup_task.xml

echo ^<?xml version="1.0" encoding="UTF-16"?^> > "%CLEANUP_XML%"
echo ^<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task"^> >> "%CLEANUP_XML%"
echo   ^<RegistrationInfo^> >> "%CLEANUP_XML%"
echo     ^<Description^>Limpieza automatica de recordatorios - Planificador IA^</Description^> >> "%CLEANUP_XML%"
echo   ^</RegistrationInfo^> >> "%CLEANUP_XML%"
echo   ^<Triggers^> >> "%CLEANUP_XML%"
echo     ^<CalendarTrigger^> >> "%CLEANUP_XML%"
echo       ^<StartBoundary^>2024-01-01T04:00:00^</StartBoundary^> >> "%CLEANUP_XML%"
echo       ^<Enabled^>true^</Enabled^> >> "%CLEANUP_XML%"
echo       ^<ScheduleByDay^> >> "%CLEANUP_XML%"
echo         ^<DaysInterval^>1^</DaysInterval^> >> "%CLEANUP_XML%"
echo       ^</ScheduleByDay^> >> "%CLEANUP_XML%"
echo     ^</CalendarTrigger^> >> "%CLEANUP_XML%"
echo   ^</Triggers^> >> "%CLEANUP_XML%"
echo   ^<Principals^> >> "%CLEANUP_XML%"
echo     ^<Principal id="Author"^> >> "%CLEANUP_XML%"
echo       ^<LogonType^>InteractiveToken^</LogonType^> >> "%CLEANUP_XML%"
echo       ^<RunLevel^>LeastPrivilege^</RunLevel^> >> "%CLEANUP_XML%"
echo     ^</Principal^> >> "%CLEANUP_XML%"
echo   ^</Principals^> >> "%CLEANUP_XML%"
echo   ^<Settings^> >> "%CLEANUP_XML%"
echo     ^<MultipleInstancesPolicy^>IgnoreNew^</MultipleInstancesPolicy^> >> "%CLEANUP_XML%"
echo     ^<DisallowStartIfOnBatteries^>false^</DisallowStartIfOnBatteries^> >> "%CLEANUP_XML%"
echo     ^<StopIfGoingOnBatteries^>false^</StopIfGoingOnBatteries^> >> "%CLEANUP_XML%"
echo     ^<AllowHardTerminate^>true^</AllowHardTerminate^> >> "%CLEANUP_XML%"
echo     ^<StartWhenAvailable^>false^</StartWhenAvailable^> >> "%CLEANUP_XML%"
echo     ^<RunOnlyIfNetworkAvailable^>false^</RunOnlyIfNetworkAvailable^> >> "%CLEANUP_XML%"
echo     ^<IdleSettings^> >> "%CLEANUP_XML%"
echo       ^<StopOnIdleEnd^>true^</StopOnIdleEnd^> >> "%CLEANUP_XML%"
echo       ^<RestartOnIdle^>false^</RestartOnIdle^> >> "%CLEANUP_XML%"
echo     ^</IdleSettings^> >> "%CLEANUP_XML%"
echo     ^<AllowStartOnDemand^>true^</AllowStartOnDemand^> >> "%CLEANUP_XML%"
echo     ^<Enabled^>true^</Enabled^> >> "%CLEANUP_XML%"
echo     ^<Hidden^>false^</Hidden^> >> "%CLEANUP_XML%"
echo     ^<RunOnlyIfIdle^>false^</RunOnlyIfIdle^> >> "%CLEANUP_XML%"
echo     ^<WakeToRun^>false^</WakeToRun^> >> "%CLEANUP_XML%"
echo     ^<ExecutionTimeLimit^>PT1H^</ExecutionTimeLimit^> >> "%CLEANUP_XML%"
echo     ^<Priority^>7^</Priority^> >> "%CLEANUP_XML%"
echo   ^</Settings^> >> "%CLEANUP_XML%"
echo   ^<Actions Context="Author"^> >> "%CLEANUP_XML%"
echo     ^<Exec^> >> "%CLEANUP_XML%"
echo       ^<Command^>cmd^</Command^> >> "%CLEANUP_XML%"
echo       ^<Arguments^>/c "cd /d "%PROJECT_DIR%" && %PYTHON_CMD% manage.py cleanup_reminders --days 30 >> logs\cleanup.log 2>&1"^</Arguments^> >> "%CLEANUP_XML%"
echo     ^</Exec^> >> "%CLEANUP_XML%"
echo   ^</Actions^> >> "%CLEANUP_XML%"
echo ^</Task^> >> "%CLEANUP_XML%"

echo 📋 Configurando tareas programadas...
echo.

:: Eliminar tareas existentes si existen
schtasks /delete /tn "PlanificadorIA_Recordatorios" /f >nul 2>&1
schtasks /delete /tn "PlanificadorIA_Limpieza" /f >nul 2>&1

:: Crear nuevas tareas
schtasks /create /xml "%TASK_XML%" /tn "PlanificadorIA_Recordatorios"
if errorlevel 1 (
    echo ❌ Error creando tarea de recordatorios
    goto :error
)

schtasks /create /xml "%CLEANUP_XML%" /tn "PlanificadorIA_Limpieza"
if errorlevel 1 (
    echo ❌ Error creando tarea de limpieza
    goto :error
)

:: Limpiar archivos temporales
del "%TASK_XML%" >nul 2>&1
del "%CLEANUP_XML%" >nul 2>&1

echo.
echo ✅ ¡Configuración completada exitosamente!
echo.
echo 📊 RESUMEN:
echo - Recordatorios: Cada 5 minutos
echo - Limpieza: Diariamente a las 4:00 AM
echo - Logs: logs\reminders.log y logs\cleanup.log
echo.
echo 💡 COMANDOS ÚTILES:
echo - Ver tareas: schtasks /query /tn "PlanificadorIA_*"
echo - Ejecutar manualmente: python manage.py send_pending_reminders
echo - Ver logs: type logs\reminders.log
echo.
pause
exit /b 0

:error
echo.
echo ❌ Error en la configuración
echo Verifica que tengas permisos de administrador
echo.
pause
exit /b 1
