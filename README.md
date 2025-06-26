# 🤖 AI-Powered Student Routine Planner

¡Bienvenido al futuro de la organización estudiantil! Este proyecto es un **Planificador de Rutinas Inteligente con IA**, una plataforma web dinámica diseñada para revolucionar la gestión del tiempo de los estudiantes mediante el poder de la Inteligencia Artificial y recordatorios automáticos inteligentes.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2+-092E20.svg)](https://www.djangoproject.com/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3-38B2AC.svg)](https://tailwindcss.com/)
[![Gmail API](https://img.shields.io/badge/Gmail_API-Google-EA4335.svg)](https://developers.google.com/gmail/api)
[![Google Calendar](https://img.shields.io/badge/Google_Calendar-API-4285F4.svg)](https://developers.google.com/calendar)

---

## 📜 Descripción del Proyecto

Este sistema avanzado, desarrollado con el robusto framework **Django**, tiene como objetivo principal optimizar el uso del tiempo de los estudiantes, equilibrando sus actividades académicas con descansos adecuados. La plataforma utiliza algoritmos de IA para ofrecer recomendaciones personalizadas, ajustes automáticos basados en los hábitos del usuario, y un **sistema de recordatorios automáticos inteligentes** que se adapta al comportamiento estudiantil.

El público objetivo son estudiantes de nivel medio y superior que deseen mejorar su organización, evitar la procrastinación y potenciar su rendimiento académico con una solución completamente automatizada y adaptativa.

## ✨ Características Principales

### 🎯 Módulos Core del Sistema

* **🔐 Autenticación y Gestión de Usuarios**
  - Registro seguro con validación de email
  - Inicio de sesión tradicional y OAuth con Google
  - Perfiles de usuario personalizables
  - Gestión de sesiones segura

* **🗓️ Gestión Inteligente de Horarios**
  - Creación y visualización de horarios dinámicos
  - Planificación automática de tareas
  - Programación inteligente de descansos
  - Vista semanal y mensual interactiva

* **🧠 Optimización con IA**
  - Algoritmos de priorización automática de tareas
  - Generación de bloques de tiempo enfocados
  - Reorganización automática del horario
  - Análisis predictivo de productividad

* **🔔 Sistema de Recordatorios Automáticos Inteligentes** ⭐ **NUEVO**
  - **Envío automático** de recordatorios por email y Google Calendar
  - **Frecuencia adaptativa** que aprende del comportamiento del usuario
  - **Personalización con IA** para generar contenido relevante
  - **Integración completa** con Gmail API y Google Calendar API
  - **Configuración multiplataforma** (Windows, Linux, macOS)
  - **Sistema de respuestas** para mejorar la personalización

* **📊 Seguimiento y Análisis Avanzado**
  - Métricas de productividad en tiempo real
  - Análisis de patrones de estudio
  - Reportes de rendimiento personalizados
  - Aprendizaje continuo de hábitos

* **❤️ Bienestar y Formación**
  - Alertas inteligentes de descanso
  - Recomendaciones de técnicas de estudio
  - Monitoreo de carga de trabajo
  - Sugerencias de equilibrio vida-estudio

## 🛠️ Tecnologías Utilizadas

Este proyecto se construyó utilizando un stack de tecnologías moderno y escalable:

### 🔧 Backend & Core
* **Framework:** Django 4.2+ (Python)
* **Base de Datos:** PostgreSQL (Producción) / SQLite (Desarrollo)
* **Autenticación:** Django Allauth + Google OAuth 2.0
* **APIs:** Django REST Framework
* **Tareas Asíncronas:** Django Management Commands + Cron/Task Scheduler

### 🎨 Frontend & UI
* **CSS Framework:** Tailwind CSS 3.0
* **JavaScript:** Vanilla JS + Alpine.js
* **Iconos:** Heroicons
* **Responsive Design:** Mobile-first approach

### 🤖 Inteligencia Artificial & Automatización
* **Machine Learning:** Scikit-learn para análisis predictivo
* **Procesamiento de Datos:** Pandas, NumPy
* **Algoritmos de IA:** Modelos personalizados para optimización de rutinas
* **Sistema de Recordatorios:** Automatización inteligente con frecuencia adaptativa

### 🔗 Integraciones Externas
* **Gmail API:** Envío automático de recordatorios por email
* **Google Calendar API:** Creación automática de eventos
* **Google Cloud Console:** Gestión de credenciales OAuth
* **Cron Jobs:** Automatización de tareas en Linux/macOS
* **Windows Task Scheduler:** Automatización en Windows

### ☁️ Despliegue & Infraestructura
* **Cloud Provider:** Amazon Web Services (AWS)
* **Almacenamiento:** AWS S3 para archivos estáticos
* **Base de Datos:** AWS RDS PostgreSQL
* **Servidor:** AWS EC2
* **CDN:** AWS CloudFront

## 🚀 Guía de Instalación y Ejecución Local

Para ejecutar este proyecto en tu máquina local, sigue estos pasos detallados:

### 1. Prerrequisitos

Asegúrate de tener instalados **Python** y **Node.js** en tu sistema. Puedes verificarlo con los siguientes comandos en tu terminal:

```bash
# Verificar la versión de Python (se recomienda 3.8 o superior)
python --version

# Verificar la versión de Node.js (se recomienda 14.x o superior)
node --version

# Verificar la versión de npm (gestor de paquetes de Node.js)
npm --version
```

### 2. Clonar el Repositorio

Primero, clona el repositorio desde GitHub a tu máquina local.

```bash
git clone https://github.com/SnayderCJ/Proyecto-final-Snayder-Cedeno.git
cd tu-repositorio
```

### 3. Configuración del Backend (Django)

Vamos a configurar el entorno virtual y las dependencias de Python.

```bash
# 1. Crear un entorno virtual para aislar las dependencias del proyecto
python -m venv venv

# 2. Activar el entorno virtual
# En Windows:
venv\Scripts\activate
# En macOS/Linux:
source venv/bin/activate

# 3. Instalar todas las dependencias de Python listadas en requirements.txt
pip install -r requirements.txt
```

### 4. Configuración del Frontend (Tailwind CSS)

Ahora, instalaremos las dependencias de Node.js para que Tailwind CSS funcione correctamente.

```bash
# Instalar las dependencias de node (tailwindcss, postcss, etc.)
npm install
```

### 5. Configuración del Sistema

#### 5.1 Variables de Entorno
La seguridad es crucial. Este proyecto usa un archivo `.env` para gestionar las variables sensibles.

1. En la raíz del proyecto, crea un archivo llamado `.env`
2. Copia el contenido del archivo `.env.example` (si existe) o usa la siguiente plantilla
3. **Completa los valores con tus propias credenciales**

```env
# Configuración de Django
SECRET_KEY='tu-super-secreta-django-key'
DEBUG=True

# Base de Datos
DATABASE_URL='postgres://user:password@host:port/dbname'

# Google OAuth 2.0 (Inicio de sesión)
GOOGLE_CLIENT_ID='tu-google-client-id'
GOOGLE_CLIENT_SECRET='tu-google-client-secret'

# Gmail API (Sistema de Recordatorios)
GMAIL_API_CREDENTIALS='path/to/credentials.json'
GMAIL_TOKEN_PATH='path/to/token.pickle'

# Google Calendar API
CALENDAR_API_CREDENTIALS='path/to/calendar_credentials.json'
CALENDAR_TOKEN_PATH='path/to/calendar_token.pickle'

# AWS (Archivos Estáticos)
AWS_ACCESS_KEY_ID='tu-aws-access-key'
AWS_SECRET_ACCESS_KEY='tu-aws-secret-key'
AWS_STORAGE_BUCKET_NAME='tu-s3-bucket-name'
```

#### 5.2 Configuración de Recordatorios Automáticos

El sistema de recordatorios requiere configuración adicional para funcionar correctamente:

1. **Configurar APIs de Google**
   ```bash
   # Instalar herramienta de línea de comandos de Google Cloud
   curl https://sdk.cloud.google.com | bash
   
   # Autenticar con Google Cloud
   gcloud auth login
   
   # Habilitar APIs necesarias
   gcloud services enable gmail.googleapis.com
   gcloud services enable calendar.googleapis.com
   ```

2. **Configurar Automatización**
   
   **En Linux/macOS:**
   ```bash
   # Dar permisos de ejecución
   chmod +x setup_reminder_crons.sh
   
   # Ejecutar script de configuración
   ./setup_reminder_crons.sh
   ```
   
   **En Windows:**
   ```batch
   # Ejecutar como administrador
   setup_reminder_scheduler_windows.bat
   ```

3. **Verificar Instalación**
   ```bash
   # Probar sistema de recordatorios
   python manage.py test_reminder_system --user testuser
   
   # Verificar envío de recordatorios pendientes
   python manage.py send_pending_reminders --dry-run
   ```

### 6. Finalizando la Configuración

Ya casi terminamos. Solo falta aplicar las migraciones de la base de datos.

```bash
# Aplicar las migraciones para crear las tablas en la base de datos
python manage.py migrate

# (Opcional pero recomendado) Crear un superusuario para acceder al admin de Django
python manage.py createsuperuser
```

### 7. ¡Ejecutar la Aplicación! ⚡️

Para correr la aplicación, necesitarás **dos terminales** abiertas simultáneamente en la raíz del proyecto.

**Terminal 1: Iniciar el proceso de Tailwind CSS**

Este comando vigilará tus archivos de plantilla y CSS para compilarlos automáticamente cada vez que hagas un cambio.

```bash
# Este comando ejecuta el script "tailwind" definido en tu package.json
npm run tailwind
```

**Terminal 2: Iniciar el servidor de Django**

Este comando pondrá en marcha el servidor de desarrollo de Django.

```bash
# ¡Asegúrate de que tu entorno virtual (venv) esté activado!
python manage.py runserver
```

¡Y listo! 🎉 Abre tu navegador web y visita **`http://127.0.0.1:8000`**. Deberías ver la página de inicio de sesión de tu aplicación.

## 🔧 Comandos Útiles del Sistema

### 📋 Gestión de Recordatorios

```bash
# Enviar recordatorios pendientes
python manage.py send_pending_reminders

# Enviar recordatorios en modo simulación (sin envío real)
python manage.py send_pending_reminders --dry-run

# Limpiar recordatorios antiguos y fallidos
python manage.py cleanup_reminders

# Sincronizar eventos del planner con recordatorios
python manage.py sync_planner_events

# Probar sistema completo de recordatorios
python manage.py test_reminder_system --user [username]

# Probar sistema sin envío de emails
python manage.py test_reminder_system --user [username] --skip-email
```

### 🗄️ Gestión de Base de Datos

```bash
# Crear y aplicar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos de prueba (si existen fixtures)
python manage.py loaddata fixtures/sample_data.json

# Hacer backup de la base de datos
python manage.py dumpdata > backup.json
```

### 🧹 Mantenimiento

```bash
# Limpiar archivos de cache de Django
python manage.py clearcache

# Recopilar archivos estáticos para producción
python manage.py collectstatic

# Verificar configuración del proyecto
python manage.py check

# Ejecutar tests
python manage.py test
```

## 📚 Documentación Adicional

### 🔗 Enlaces Importantes

- **[Documentación de Recordatorios Automáticos](RECORDATORIOS_AUTOMATICOS.md)** - Guía completa del sistema de recordatorios
- **[Django Documentation](https://docs.djangoproject.com/)** - Documentación oficial de Django
- **[Tailwind CSS](https://tailwindcss.com/docs)** - Documentación de Tailwind CSS
- **[Gmail API](https://developers.google.com/gmail/api)** - Documentación de Gmail API
- **[Google Calendar API](https://developers.google.com/calendar)** - Documentación de Google Calendar API

### 🚨 Solución de Problemas Comunes

#### Error: "No module named 'X'"
```bash
# Asegúrate de que el entorno virtual esté activado
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

#### Error: "Gmail API not configured"
```bash
# Verificar credenciales de Gmail API
python manage.py test_gmail

# Reconfigurar credenciales si es necesario
# Seguir la guía en RECORDATORIOS_AUTOMATICOS.md
```

#### Error: "Database connection failed"
```bash
# Verificar configuración de base de datos en .env
# Para desarrollo, usar SQLite (por defecto)
# Para producción, configurar PostgreSQL
```

#### Recordatorios no se envían automáticamente
```bash
# Verificar que los cron jobs estén configurados
crontab -l  # Linux/macOS

# En Windows, verificar Task Scheduler
# Ejecutar manualmente para probar
python manage.py send_pending_reminders
```

### 🔒 Consideraciones de Seguridad

- **Nunca** subas el archivo `.env` al repositorio
- Usa **HTTPS** en producción
- Configura **CORS** apropiadamente para APIs
- Mantén las **dependencias actualizadas**
- Usa **variables de entorno** para datos sensibles
- Configura **rate limiting** para APIs públicas

### 🚀 Despliegue en Producción

Para desplegar en producción, considera:

1. **Configurar DEBUG=False** en el archivo `.env`
2. **Usar PostgreSQL** como base de datos
3. **Configurar ALLOWED_HOSTS** apropiadamente
4. **Usar un servidor web** como Nginx + Gunicorn
5. **Configurar SSL/TLS** para HTTPS
6. **Configurar monitoreo** y logs
7. **Hacer backup** regular de la base de datos

### 📈 Métricas y Monitoreo

El sistema incluye logging automático para:

- ✅ Recordatorios enviados exitosamente
- ❌ Errores en el envío de recordatorios
- 📊 Estadísticas de uso por usuario
- 🔄 Cambios en la frecuencia adaptativa
- 📝 Actividad general del sistema

## 🖼️ Vistas Previas de la Aplicación

A continuación, puedes ver cómo luce el **Planificador de Rutinas Inteligente** en acción:

| Pantalla                                   | Vista                                                                                                                                                                                                                                         | Descripción                                                                                                 |
|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| **Inicio de Sesión y Registro**             | ![Interfaz de Login](https://media.discordapp.net/attachments/1248680132865036310/1384005980857303100/image.png?ex=6850db83&is=684f8a03&hm=888ad2766f5ec5e24ad3ad3e0d7f8458a1e1168839a256dbb9a78ab2ffb301e4&=&format=webp&quality=lossless&width=160&height=220) | Acceso seguro para estudiantes, con opción de registro y login rápido.                                      |
| **Dashboard Principal**                     | ![Dashboard](https://media.discordapp.net/attachments/1248680132865036310/1384006249070461028/image.png?ex=6850dbc3&is=684f8a43&hm=e5cf4584b194c777d2aee505e42eb3c33616b4679a340139cf1e88be27af9828&=&format=webp&quality=lossless&width=260&height=120)      | Vista central donde el estudiante visualiza su rutina, progreso y recomendaciones inteligentes.              |
| **Gestión de Tareas y Calendario Inteligente** | ![Gestión de Tareas](https://media.discordapp.net/attachments/1248680132865036310/1384006389667729571/image.png?ex=6850dbe4&is=684f8a64&hm=bd8994d8f5a8b8ffc2a6f91d11453eb96da03638d23637abf09660d9fcd2450a&=&format=webp&quality=lossless&width=200&height=120) | Herramienta para organizar tareas, visualizar el calendario y recibir sugerencias automáticas.               |

---

<details>
<summary>Ver imágenes en tamaño completo</summary>

**Interfaz de Inicio de Sesión y Registro**  
![Interfaz de Login](https://media.discordapp.net/attachments/1248680132865036310/1384005980857303100/image.png?ex=6850db83&is=684f8a03&hm=888ad2766f5ec5e24ad3ad3e0d7f8458a1e1168839a256dbb9a78ab2ffb301e4&=&format=webp&quality=lossless&width=394&height=556)  
_Ilustración 1: interfaz de usuario login_

**Dashboard Principal del Estudiante**  
![Dashboard](https://media.discordapp.net/attachments/1248680132865036310/1384006249070461028/image.png?ex=6850dbc3&is=684f8a43&hm=e5cf4584b194c777d2aee505e42eb3c33616b4679a340139cf1e88be27af9828&=&format=webp&quality=lossless&width=1237&height=559)  
_Ilustración 3: interfaz de usuario Dashboard_

**Gestión de Tareas y Calendario Inteligente**  
![Gestión de Tareas](https://media.discordapp.net/attachments/1248680132865036310/1384006389667729571/image.png?ex=6850dbe4&is=684f8a64&hm=bd8994d8f5a8b8ffc2a6f91d11453eb96da03638d23637abf09660d9fcd2450a&=&format=webp&quality=lossless&width=959&height=562)  
_Ilustración 4: interfaz de usuario Gestión de tareas y Calendario_

</details>

## 🧑‍💻 Autores

Este proyecto fue desarrollado con dedicación por los siguientes estudiantes de la carrera de Software en la UNEMI:

* **Mayerly Anabela Piloso Muñoz**
* **Oswaldo Danilo Angulo Tamayo**
* **Jostyn Snayder Cedeño Jimenez** (Gerente del Proyecto)

Bajo la supervisión del docente Ing. Rodrigo Josue Guevara Reyes.

## 📄 Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.