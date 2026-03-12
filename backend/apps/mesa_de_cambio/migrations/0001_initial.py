from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MesaDeCambioOperacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('codigo_ente_supervisado', models.CharField(max_length=4)),
                ('codigo_identificacion_operacion', models.CharField(max_length=20, unique=True)),
                ('fecha_operacion', models.DateTimeField()),
                ('identificacion_cliente', models.CharField(max_length=20)),
                ('nombre_cliente', models.CharField(max_length=100)),
                ('actividad_economica_cliente', models.CharField(max_length=10)),
                ('moneda', models.IntegerField()),
                ('monto_divisa', models.DecimalField(decimal_places=4, max_digits=20)),
                ('tipo_cambio_bs', models.DecimalField(decimal_places=4, max_digits=20)),
                ('contravalor_bs', models.DecimalField(decimal_places=4, max_digits=20)),
                ('codigo_cuenta_moneda_nacional', models.CharField(default='0', max_length=20)),
                ('tipo_cuenta_moneda_nacional', models.IntegerField(default=0)),
                ('codigo_cuenta_moneda_extranjera', models.CharField(default='0', max_length=20)),
                ('tipo_cuenta_moneda_extranjera', models.IntegerField(default=0)),
                ('destino_fondos', models.IntegerField()),
                ('medio_pago', models.IntegerField()),
                ('status', models.CharField(
                    choices=[
                        ('pending', 'Pendiente'),
                        ('sent', 'Enviado'),
                        ('success', 'Exitoso'),
                        ('rejected', 'Rechazado'),
                        ('corrected', 'Corregido'),
                        ('failed', 'Fallido'),
                    ],
                    default='pending',
                    max_length=20,
                )),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('error_code', models.IntegerField(blank=True, null=True)),
                ('error_detail', models.TextField(blank=True, null=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('last_sent_at', models.DateTimeField(blank=True, null=True)),
                ('response_data', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'mesa_de_cambio_operaciones',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='mesadecambiooperacion',
            index=models.Index(fields=['status'], name='mesa_de_ca_status_idx'),
        ),
        migrations.AddIndex(
            model_name='mesadecambiooperacion',
            index=models.Index(fields=['fecha_operacion'], name='mesa_de_ca_fecha_idx'),
        ),
        migrations.AddIndex(
            model_name='mesadecambiooperacion',
            index=models.Index(fields=['codigo_identificacion_operacion'], name='mesa_de_ca_codigo_idx'),
        ),
    ]
