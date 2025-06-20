# Generated by Django 5.2.1 on 2025-06-15 20:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título del Evento')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Descripción')),
                ('event_type', models.CharField(choices=[('tarea', 'Tarea/Estudio'), ('clase', 'Clase/Académico'), ('descanso', 'Descanso'), ('personal', 'Personal'), ('otro', 'Otro')], default='tarea', max_length=20, verbose_name='Tipo de Evento')),
                ('priority', models.CharField(choices=[('alta', 'Alta'), ('media', 'Media'), ('baja', 'Baja')], default='media', max_length=10, verbose_name='Prioridad')),
                ('start_time', models.DateTimeField(verbose_name='Hora de Inicio')),
                ('end_time', models.DateTimeField(verbose_name='Hora de Fin')),
                ('due_date', models.DateField(blank=True, null=True, verbose_name='Fecha de Vencimiento')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Completado')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Última Actualización')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL, verbose_name='Usuario')),
            ],
            options={
                'verbose_name': 'Evento',
                'verbose_name_plural': 'Eventos',
                'ordering': ['start_time', 'priority'],
            },
        ),
    ]
