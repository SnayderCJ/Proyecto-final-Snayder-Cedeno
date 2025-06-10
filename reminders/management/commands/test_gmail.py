# reminders/management/commands/test_gmail.py - CORREGIDO para Windows
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reminders.models import Reminder, ReminderConfiguration
from reminders.services.gmail_service import gmail_service
from django.utils import timezone
import os

class Command(BaseCommand):
    help = 'Diagnóstico completo del sistema de recordatorios'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--send-test',
            action='store_true',
            help='Enviar recordatorio de prueba real',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Username del usuario para la prueba',
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Iniciando diagnóstico del sistema de recordatorios...\n'))
        
        # 1. Verificar archivos OAuth
        self.check_oauth_files()
        
        # 2. Verificar Gmail Service
        self.check_gmail_service()
        
        # 3. Verificar usuarios y configuración
        self.check_users_config()
        
        # 4. Verificar templates
        self.check_templates()
        
        # 5. Verificar configuración de Django
        self.check_django_config()
        
        # 6. Enviar prueba real si se solicita
        if options['send_test']:
            username = options.get('user')
            if not username:
                self.stdout.write('ERROR: Debes especificar un usuario con --user USERNAME')
                self.stdout.write('Usuarios disponibles:')
                for user in User.objects.all()[:10]:
                    self.stdout.write(f'  - {user.username} ({user.email or "sin email"})')
                return
            
            self.send_test_email(username)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Diagnóstico completado'))
    
    def check_oauth_files(self):
        self.stdout.write('📁 Verificando archivos OAuth...')
        
        from django.conf import settings
        base_dir = settings.BASE_DIR
        
        # Verificar credenciales
        credentials_path = os.path.join(base_dir, 'studiFly_desktop_client.json')
        if os.path.exists(credentials_path):
            self.stdout.write(f'   ✅ Credenciales encontradas: studiFly_desktop_client.json')
            # Leer y verificar contenido
            try:
                import json
                with open(credentials_path, 'r') as f:
                    creds = json.load(f)
                    client_id = creds.get('installed', {}).get('client_id', 'No encontrado')
                    self.stdout.write(f'   🔑 Client ID: {client_id[:20]}...')
            except Exception as e:
                self.stdout.write(f'   ⚠️ Error al leer credenciales: {e}')
        else:
            self.stdout.write(f'   ❌ Credenciales NO encontradas: {credentials_path}')
        
        # Verificar token
        token_path = os.path.join(base_dir, 'token.json')
        if os.path.exists(token_path):
            self.stdout.write(f'   ✅ Token encontrado: token.json')
            # Verificar fecha de modificación
            import datetime
            mod_time = os.path.getmtime(token_path)
            mod_date = datetime.datetime.fromtimestamp(mod_time)
            self.stdout.write(f'   📅 Última actualización: {mod_date.strftime("%d/%m/%Y %H:%M:%S")}')
            
            # Verificar scopes en el token
            try:
                import json
                with open(token_path, 'r') as f:
                    token_data = json.load(f)
                    scopes = token_data.get('scopes', [])
                    self.stdout.write(f'   🔐 Scopes en token: {len(scopes)} encontrados')
                    required_scopes = [
                        'https://www.googleapis.com/auth/gmail.send',
                        'https://www.googleapis.com/auth/gmail.readonly',
                        'https://www.googleapis.com/auth/calendar'
                    ]
                    missing_scopes = [scope for scope in required_scopes if scope not in scopes]
                    if missing_scopes:
                        self.stdout.write(f'   ⚠️ Scopes faltantes: {len(missing_scopes)}')
                        for scope in missing_scopes:
                            self.stdout.write(f'      - {scope}')
                        self.stdout.write('   💡 Elimina token.json para regenerar con nuevos scopes')
                    else:
                        self.stdout.write('   ✅ Todos los scopes requeridos presentes')
            except Exception as e:
                self.stdout.write(f'   ⚠️ Error al verificar scopes: {e}')
        else:
            self.stdout.write(f'   ⚠️ Token NO encontrado: token.json')
            self.stdout.write(f'   💡 Se creará automáticamente en el primer uso')
    
    def check_gmail_service(self):
        self.stdout.write('\n📧 Verificando Gmail Service...')
        
        if gmail_service is None:
            self.stdout.write('   ❌ Gmail Service NO inicializado')
            self.stdout.write('   💡 Revisa los archivos OAuth y scopes')
            self.stdout.write('   🔧 Para solucionarlo:')
            self.stdout.write('      1. Elimina token.json')
            self.stdout.write('      2. Ejecuta este comando de nuevo')
            self.stdout.write('      3. Acepta todos los permisos en el navegador')
            return
        
        try:
            # Probar Gmail
            if gmail_service.gmail_service:
                profile = gmail_service.gmail_service.users().getProfile(userId='me').execute()
                email = profile.get('emailAddress')
                self.stdout.write(f'   ✅ Gmail conectado: {email}')
                
                # Verificar que sea el mismo email de settings
                from django.conf import settings
                default_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'No configurado')
                if email in default_email:
                    self.stdout.write('   ✅ Email coincide con DEFAULT_FROM_EMAIL')
                else:
                    self.stdout.write(f'   ⚠️ Email no coincide. DEFAULT_FROM_EMAIL: {default_email}')
            else:
                self.stdout.write('   ❌ Gmail Service no disponible')
            
            # Probar Calendar
            if gmail_service.calendar_service:
                calendars = gmail_service.calendar_service.calendarList().list().execute()
                count = len(calendars.get('items', []))
                self.stdout.write(f'   ✅ Calendar conectado: {count} calendarios disponibles')
                
                # Mostrar calendario principal
                for cal in calendars.get('items', [])[:3]:
                    name = cal.get('summary', 'Sin nombre')
                    is_primary = '(Principal)' if cal.get('primary') else ''
                    self.stdout.write(f'      📅 {name} {is_primary}')
            else:
                self.stdout.write('   ❌ Calendar Service no disponible')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Error en servicios Google: {str(e)}')
            if 'insufficient' in str(e).lower() or 'scope' in str(e).lower():
                self.stdout.write('   💡 Error de scopes insuficientes')
                self.stdout.write('   🔧 Para solucionarlo:')
                self.stdout.write('      1. Elimina token.json')
                self.stdout.write('      2. Ejecuta: python manage.py test_gmail')
                self.stdout.write('      3. En el navegador, acepta TODOS los permisos')
            else:
                self.stdout.write('   💡 Intenta eliminar token.json y volver a autenticar')
    
    def check_users_config(self):
        self.stdout.write('\n👥 Verificando usuarios y configuración...')
        
        users = User.objects.all()
        self.stdout.write(f'   📊 Total usuarios: {users.count()}')
        
        if users.count() == 0:
            self.stdout.write('   ⚠️ No hay usuarios registrados')
            self.stdout.write('   💡 Crea un superusuario: python manage.py createsuperuser')
            return
        
        for user in users[:5]:  # Mostrar solo los primeros 5
            self.stdout.write(f'\n   👤 Usuario: {user.username}')
            self.stdout.write(f'      📧 Email: {user.email or "❌ Sin email"}')
            self.stdout.write(f'      👤 Nombre: {user.get_full_name() or "Sin nombre completo"}')
            self.stdout.write(f'      🔐 Staff: {"✅" if user.is_staff else "❌"}')
            self.stdout.write(f'      🏃 Activo: {"✅" if user.is_active else "❌"}')
            
            # Verificar configuración
            try:
                config = user.reminder_config
                self.stdout.write(f'      ⚙️ Config: ✅ Activa')
                self.stdout.write(f'         📧 Email habilitado: {"✅" if config.email_enabled else "❌"}')
                self.stdout.write(f'         📅 Calendar habilitado: {"✅" if config.calendar_enabled else "❌"}')
                self.stdout.write(f'         🔔 Recordatorios: {"✅" if config.reminders_enabled else "❌"}')
                self.stdout.write(f'         📊 Frecuencia: {config.get_current_frequency_display()}')
            except:
                self.stdout.write(f'      ⚙️ Config: ❌ Sin configuración (se creará automáticamente)')
            
            # Verificar recordatorios
            reminders_count = user.reminders.count()
            pending_count = user.reminders.filter(status='pending').count()
            self.stdout.write(f'      📋 Recordatorios: {reminders_count} total, {pending_count} pendientes')
    
    def check_templates(self):
        self.stdout.write('\n📄 Verificando templates...')
        
        from django.template.loader import get_template
        from django.conf import settings
        
        # Mostrar configuración de templates
        template_dirs = settings.TEMPLATES[0]['DIRS']
        self.stdout.write(f'   📁 Directorios de templates: {template_dirs}')
        
        templates_to_check = [
            'reminder_email.html',  # Tu estructura directa
            'reminder_list.html',
            'create_reminder.html', 
            'configuration.html',
            'base.html',
        ]
        
        for template_name in templates_to_check:
            try:
                template = get_template(template_name)
                self.stdout.write(f'   ✅ {template_name}')
            except Exception as e:
                self.stdout.write(f'   ❌ {template_name}: {str(e)}')
                if template_name == 'reminder_email.html':
                    self.stdout.write('   💡 Crea el archivo reminders/templates/reminder_email.html')
                elif template_name == 'configuration.html':
                    self.stdout.write('   💡 Hay un error en la sintaxis del template')
    
    def check_django_config(self):
        self.stdout.write('\n⚙️ Verificando configuración de Django...')
        
        from django.conf import settings
        
        # Verificar configuraciones importantes
        configs = [
            ('SITE_URL', getattr(settings, 'SITE_URL', 'No configurado')),
            ('DEFAULT_FROM_EMAIL', getattr(settings, 'DEFAULT_FROM_EMAIL', 'No configurado')),
            ('TIME_ZONE', getattr(settings, 'TIME_ZONE', 'UTC')),
            ('USE_TZ', getattr(settings, 'USE_TZ', False)),
            ('EMAIL_HOST_USER', getattr(settings, 'EMAIL_HOST_USER', 'No configurado')),
        ]
        
        for key, value in configs:
            status = '✅' if value != 'No configurado' else '❌'
            self.stdout.write(f'   {status} {key}: {value}')
        
        # Verificar apps instaladas
        apps = settings.INSTALLED_APPS
        required_apps = ['reminders', 'django.contrib.messages']
        
        for app in required_apps:
            if any(app in installed_app for installed_app in apps):
                self.stdout.write(f'   ✅ App instalada: {app}')
            else:
                self.stdout.write(f'   ❌ App faltante: {app}')
    
# En reminders/management/commands/test_gmail.py
# REEMPLAZA la función send_test_email con esta versión CORREGIDA:

    def send_test_email(self, username):
        self.stdout.write(f'\n🧪 Enviando email de prueba a usuario: {username}')
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'   ✅ Usuario encontrado: {user.email}')
            
            if not user.email:
                self.stdout.write('   ❌ Usuario sin email configurado')
                return
            
            # Obtener configuración ACTUAL del usuario
            config, created = ReminderConfiguration.objects.get_or_create(user=user)
            if created:
                self.stdout.write('   ✅ Configuración creada automáticamente')
            
            # Mostrar configuración actual
            self.stdout.write(f'   📧 Email habilitado: {config.email_enabled}')
            self.stdout.write(f'   📅 Calendar habilitado: {config.calendar_enabled}')
            self.stdout.write(f'   🔔 Tipo preferido: {config.get_preferred_type_display()}')
            
            # USAR LA CONFIGURACIÓN ACTUAL DEL USUARIO
            reminder_type = config.preferred_type if config.preferred_type else 'email'
            
            # Crear recordatorio de prueba con configuración actual
            reminder = Reminder.objects.create(
                user=user,
                title='🧪 Prueba de Sistema - Comando Diagnóstico',
                description='Este recordatorio fue creado por el comando de diagnóstico y usa tu configuración actual.',
                target_datetime=timezone.now() + timezone.timedelta(hours=1),
                reminder_type=reminder_type,  # ← USAR CONFIGURACIÓN ACTUAL
                timing='immediate'
            )
            
            self.stdout.write(f'   ✅ Recordatorio creado: {reminder.id}')
            self.stdout.write(f'   📧 Tipo configurado: {reminder.get_reminder_type_display()}')
            
            # Enviar email
            if not gmail_service:
                self.stdout.write('   ❌ Gmail Service no disponible')
                reminder.delete()
                return
            
            # Determinar si crear calendario según configuración
            create_calendar = (
                config.calendar_enabled and 
                reminder.reminder_type in ['calendar', 'both']
            )
            
            self.stdout.write(f'   📅 Crear Calendar: {create_calendar}')
            
            result = gmail_service.send_reminder_email_with_calendar(
                reminder=reminder,
                ai_subject='🧪 Prueba de Sistema - Diagnóstico Exitoso',
                ai_description=f'''
                <div style="background: #d4edda; padding: 20px; border-radius: 10px; border-left: 4px solid #28a745;">
                    <h3 style="color: #155724; margin-top: 0;">✅ ¡Sistema Funcionando Correctamente!</h3>
                    <p style="color: #155724; margin: 0;">
                        Este email confirma que tu sistema de recordatorios está configurado correctamente.
                    </p>
                    <p style="color: #155724; margin: 10px 0 0 0;">
                        <strong>Configuración aplicada:</strong><br>
                        • Email: {'✅ Activo' if config.email_enabled else '❌ Desactivado'}<br>
                        • Calendar: {'✅ Activo' if config.calendar_enabled else '❌ Desactivado'}<br>
                        • Tipo: {reminder.get_reminder_type_display()}<br>
                        • Usuario: {user.username} ({user.email})
                    </p>
                    <p style="color: #155724; margin: 10px 0 0 0;">
                        <strong>Diagnóstico completado:</strong> {timezone.now().strftime("%d/%m/%Y %H:%M:%S")}
                    </p>
                </div>
                ''',
                create_calendar_event=create_calendar
            )
            
            if result['success']:
                self.stdout.write(f'   ✅ Email enviado exitosamente!')
                self.stdout.write(f'   📧 ID del mensaje: {result.get("email_id", "N/A")}')
                if result.get('calendar_event_id'):
                    self.stdout.write(f'   📅 Evento Calendar: {result.get("calendar_event_id")}')
                    self.stdout.write('   🎉 ¡Email + Calendar funcionando!')
                else:
                    self.stdout.write('   📧 Solo email enviado (según configuración)')
                self.stdout.write(f'   📬 Revisa tu bandeja: {user.email}')
            else:
                self.stdout.write(f'   ❌ Error al enviar: {result.get("error", "Error desconocido")}')
            
            # Limpiar recordatorio de prueba
            reminder.delete()
            self.stdout.write('   🗑️ Recordatorio de prueba eliminado')
            
        except User.DoesNotExist:
            self.stdout.write(f'   ❌ Usuario "{username}" no encontrado')
            self.stdout.write('   💡 Usuarios disponibles:')
            for user in User.objects.all()[:10]:
                self.stdout.write(f'      - {user.username} ({user.email or "sin email"})')
        
        except Exception as e:
            self.stdout.write(f'   ❌ Error inesperado: {str(e)}')
            import traceback
            self.stdout.write(f'   🔍 Traceback: {traceback.format_exc()}')