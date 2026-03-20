from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='EnteSupervisadoCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=4, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.TextField(blank=True, default='')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_selectable', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Ente supervisado',
                'verbose_name_plural': 'Entes supervisados',
                'db_table': 'core_entes_supervisados_catalog',
                'ordering': ['sort_order', 'code'],
            },
        ),
        migrations.CreateModel(
            name='MecanismoCambiarioCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=2, unique=True)),
                ('name', models.CharField(max_length=150)),
                ('description', models.TextField(blank=True, default='')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_selectable', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Mecanismo cambiario',
                'verbose_name_plural': 'Mecanismos cambiarios',
                'db_table': 'core_mecanismos_cambiarios_catalog',
                'ordering': ['sort_order', 'code'],
            },
        ),
        migrations.CreateModel(
            name='MonedaCatalog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('code', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=10)),
                ('description', models.TextField(blank=True, default='')),
                ('sort_order', models.PositiveIntegerField(default=0)),
                ('is_selectable', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Moneda',
                'verbose_name_plural': 'Monedas',
                'db_table': 'core_monedas_catalog',
                'ordering': ['sort_order', 'code'],
            },
        ),
    ]
