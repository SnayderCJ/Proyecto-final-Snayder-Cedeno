# Generated by Django 5.2.1 on 2025-06-19 05:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0002_event_category'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BloqueEstudio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('estudio', 'Estudio'), ('descanso', 'Descanso')], default='estudio', max_length=10)),
                ('fecha', models.DateField(auto_now_add=True)),
                ('hora_inicio', models.TimeField()),
                ('hora_fin', models.TimeField()),
                ('duracion_min', models.IntegerField()),
                ('completado', models.BooleanField(default=False)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
