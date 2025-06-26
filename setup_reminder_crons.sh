#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Obtener directorio del proyecto
PROJECT_DIR="$(pwd)"
PYTHON_PATH="python"
TEMP_CRON=$(mktemp)

echo -e "${YELLOW}🔄 Configurando sistema de recordatorios...${NC}"

# Verificar que los comandos necesarios existen
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

# Crear directorio de logs si no existe
mkdir -p logs
touch logs/reminders.log
touch logs/cleanup.log
chmod 666 logs/reminders.log
chmod 666 logs/cleanup.log

# Configurar crontab
crontab -l > $TEMP_CRON 2>/dev/null

# Eliminar entradas anteriores si existen
sed -i '/send_pending_reminders/d' $TEMP_CRON
sed -i '/cleanup_reminders/d' $TEMP_CRON

# Agregar nuevas entradas
echo "# Recordatorios automáticos - Configurado el $(date '+%Y-%m-%d %H:%M:%S')" >> $TEMP_CRON
echo "*/5 * * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py send_pending_reminders >> logs/reminders.log 2>&1" >> $TEMP_CRON
echo "0 4 * * * cd $PROJECT_DIR && $PYTHON_PATH manage.py cleanup_reminders --days 30 >> logs/cleanup.log 2>&1" >> $TEMP_CRON

# Instalar nuevo crontab
crontab $TEMP_CRON
rm $TEMP_CRON

echo -e "\n${GREEN}✨ Configuración completada${NC}"
echo -e "${YELLOW}💡 Tip: Revisa los logs en logs/reminders.log y logs/cleanup.log${NC}"
