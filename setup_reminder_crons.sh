#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Configurando cronjobs para recordatorios automáticos...${NC}\n"

# Obtener el directorio actual del proyecto
PROJECT_DIR=$(pwd)
PYTHON_PATH=$(which python)
VENV_PATH="$PROJECT_DIR/venv/bin/python"

# Usar el python del virtualenv si existe
if [ -f "$VENV_PATH" ]; then
    PYTHON_PATH=$VENV_PATH
    echo -e "${GREEN}✅ Usando Python del virtualenv: $PYTHON_PATH${NC}"
else
    echo -e "${YELLOW}⚠️ No se encontró virtualenv, usando Python del sistema: $PYTHON_PATH${NC}"
fi

# Verificar que los comandos existen
echo -e "\n${GREEN}🔍 Verificando comandos...${NC}"

$PYTHON_PATH manage.py send_pending_reminders --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Comando send_pending_reminders disponible${NC}"
else
    echo -e "${RED}❌ Error: Comando send_pending_reminders no encontrado${NC}"
    exit 1
fi

$PYTHON_PATH manage.py cleanup_reminders --help > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Comando cleanup_reminders disponible${NC}"
else
    echo -e "${RED}❌ Error: Comando cleanup_reminders no encontrado${NC}"
    exit 1
fi

# Crear archivo temporal para crontab
TEMP_CRON=$(mktemp)

# Respaldar crontab actual
crontab -l > $TEMP_CRON 2>/dev/null

# Eliminar entradas anteriores de recordatorios si existen
sed -i '/send_pending_reminders/d' $TEMP_CRON
sed -i '/cleanup_reminders/d' $TEMP_CRON

echo -e "\n${GREEN}📝 Agregando nuevos cronjobs...${NC}"

# Agregar nuevos cronjobs
echo "# Recordatorios automáticos - Configurado el $(date '+%Y-%m-%d %H:%M:%S')" >> $TEMP_CRON
echo "*/5 * * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py send_pending_reminders >> $PROJECT_DIR/logs/reminders.log 2>&1" >> $TEMP_CRON
echo "0 4 * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py cleanup_reminders --days 30 >> $PROJECT_DIR/logs/cleanup.log 2>&1" >> $TEMP_CRON

# Crear directorio de logs si no existe
mkdir -p $PROJECT_DIR/logs
touch $PROJECT_DIR/logs/reminders.log
touch $PROJECT_DIR/logs/cleanup.log
chmod 666 $PROJECT_DIR/logs/reminders.log
chmod 666 $PROJECT_DIR/logs/cleanup.log

# Instalar nuevo crontab
if crontab $TEMP_CRON; then
    echo -e "${GREEN}✅ Cronjobs instalados exitosamente${NC}"
    echo -e "\n${GREEN}📋 Cronjobs configurados:${NC}"
    echo -e "${YELLOW}➜ Envío de recordatorios: Cada 5 minutos${NC}"
    echo -e "${YELLOW}➜ Limpieza de recordatorios: Diariamente a las 4 AM${NC}"
else
    echo -e "${RED}❌ Error al instalar cronjobs${NC}"
    exit 1
fi

# Limpiar archivo temporal
rm $TEMP_CRON

echo -e "\n${GREEN}📊 Resumen:${NC}"
echo -e "📁 Directorio del proyecto: $PROJECT_DIR"
echo -e "🐍 Python: $PYTHON_PATH"
echo -e "📝 Logs en: $PROJECT_DIR/logs/"

echo -e "\n${GREEN}✨ Configuración completada${NC}"
echo -e "${YELLOW}💡 Tip: Revisa los logs en logs/reminders.log y logs/cleanup.log${NC}"
