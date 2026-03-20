from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_intervencion_catalogs'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActividadEconomicaCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, default='')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_selectable', models.BooleanField(default=True)),
                ('code', models.CharField(max_length=4, unique=True)),
            ],
            options={
                'verbose_name': 'Actividad económica',
                'verbose_name_plural': 'Actividades económicas',
                'db_table': 'core_actividades_economicas_catalog',
                'ordering': ['sort_order', 'code'],
                'abstract': False,
            },
        ),
    ]