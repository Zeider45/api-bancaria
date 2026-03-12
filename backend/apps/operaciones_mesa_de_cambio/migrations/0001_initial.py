from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OperacionMesaDeCambio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_active', models.BooleanField(default=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('identificacion_ente_supervisado', models.CharField(max_length=99)),
                ('tipo_pacto', models.CharField(max_length=99)),
                ('moneda', models.CharField(max_length=99)),
                ('fecha_pacto', models.DateTimeField()),
                ('monto_divisa', models.DecimalField(decimal_places=4, max_digits=20)),
                ('tipo_cambio_bs', models.DecimalField(decimal_places=4, max_digits=20)),
                ('contravalor_bs', models.DecimalField(decimal_places=4, max_digits=20)),
                ('identificacion_cliente_oferente', models.CharField(max_length=20)),
                ('nombre_cliente_oferente', models.CharField(max_length=100)),
                ('actividad_economica_cliente_oferente', models.CharField(max_length=99)),
                ('codigo_cuenta_moneda_nacional_oferente', models.CharField(max_length=20)),
                ('tipo_cuenta_moneda_nacional_cliente_oferente', models.IntegerField()),
                ('codigo_cuenta_moneda_extranjera_oferente', models.CharField(max_length=20)),
                ('tipo_cuenta_moneda_extranjera_cliente_oferente', models.IntegerField()),
                ('origen_fondos', models.CharField(max_length=99)),
                ('medio_pago_oferente', models.CharField(max_length=99)),
                ('identificacion_cliente_demandante', models.CharField(max_length=20)),
                ('nombre_cliente_demandante', models.CharField(max_length=100)),
                ('actividad_economica_cliente_demandante', models.CharField(max_length=99)),
                ('codigo_cuenta_moneda_nacional_demandante', models.CharField(max_length=20)),
                ('tipo_cuenta_moneda_nacional_cliente_demandante', models.IntegerField()),
                ('codigo_cuenta_moneda_extranjera_demandante', models.CharField(max_length=20)),
                ('tipo_cuenta_moneda_extranjera_cliente_demandante', models.IntegerField()),
                ('destino_fondos', models.CharField(max_length=99)),
                ('medio_pago_demandante', models.CharField(max_length=99)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('sent', 'Enviado'), ('success', 'Exitoso'), ('rejected', 'Rechazado'), ('corrected', 'Corregido'), ('failed', 'Fallido')], default='pending', max_length=20)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('error_code', models.IntegerField(blank=True, null=True)),
                ('error_detail', models.TextField(blank=True, null=True)),
                ('retry_count', models.IntegerField(default=0)),
                ('last_sent_at', models.DateTimeField(blank=True, null=True)),
                ('response_data', models.JSONField(blank=True, null=True)),
            ],
            options={
                'db_table': 'operaciones_mesa_de_cambio',
                'ordering': ['-created_at'],
                'indexes': [models.Index(fields=['status'], name='operaciones_status_9d8234_idx'), models.Index(fields=['fecha_pacto'], name='operaciones_fecha_p_1e196c_idx'), models.Index(fields=['identificacion_cliente_oferente'], name='operaciones_identif_d15cd3_idx'), models.Index(fields=['identificacion_cliente_demandante'], name='operaciones_identif_cb0465_idx')],
            },
        ),
    ]
