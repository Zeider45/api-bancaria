from django.db import models
from apps.core.models import BaseModel, TransactionStatus
from decimal import Decimal


class OperacionMesaDeCambio(BaseModel):
    """
    Model for Operaciones Mesa de Cambio transactions.
    Manages and validates foreign exchange desk transactions.
    """

    # Identificación de la operación (API-04)
    codigo_operacion = models.CharField(
        max_length=40,
        default='',
        blank=True,
        help_text="Código de identificación único de la operación (API-04)"
    )

    # Ente Supervisado
    identificacion_ente_supervisado = models.CharField(max_length=99)

    # Datos del pacto
    tipo_pacto = models.CharField(max_length=99)
    moneda = models.CharField(max_length=99)
    fecha_pacto = models.DateTimeField()

    # Montos
    monto_divisa = models.DecimalField(max_digits=20, decimal_places=4)
    tipo_cambio_bs = models.DecimalField(max_digits=20, decimal_places=4)
    contravalor_bs = models.DecimalField(max_digits=20, decimal_places=4)

    # Cliente Oferente
    identificacion_cliente_oferente = models.CharField(max_length=20)
    nombre_cliente_oferente = models.CharField(max_length=100)
    actividad_economica_cliente_oferente = models.CharField(max_length=99)
    codigo_cuenta_moneda_nacional_oferente = models.CharField(max_length=20)
    tipo_cuenta_moneda_nacional_cliente_oferente = models.IntegerField()  # 8, 9 or 10
    codigo_cuenta_moneda_extranjera_oferente = models.CharField(max_length=20)
    tipo_cuenta_moneda_extranjera_cliente_oferente = models.IntegerField()  # 31 or 32
    origen_fondos = models.CharField(max_length=99)
    medio_pago_oferente = models.CharField(max_length=99)

    # Cliente Demandante
    identificacion_cliente_demandante = models.CharField(max_length=20)
    nombre_cliente_demandante = models.CharField(max_length=100)
    actividad_economica_cliente_demandante = models.CharField(max_length=99)
    codigo_cuenta_moneda_nacional_demandante = models.CharField(max_length=20)
    tipo_cuenta_moneda_nacional_cliente_demandante = models.IntegerField()  # 8, 9 or 10
    codigo_cuenta_moneda_extranjera_demandante = models.CharField(max_length=20)
    tipo_cuenta_moneda_extranjera_cliente_demandante = models.IntegerField()  # 31 or 32
    destino_fondos = models.CharField(max_length=99)
    medio_pago_demandante = models.CharField(max_length=99)

    # System fields
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING,
    )
    external_id = models.CharField(max_length=100, null=True, blank=True)
    error_code = models.IntegerField(null=True, blank=True)
    error_detail = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'operaciones_mesa_de_cambio'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fecha_pacto']),
            models.Index(fields=['identificacion_cliente_oferente']),
            models.Index(fields=['identificacion_cliente_demandante']),
        ]

    def __str__(self):
        return (
            f"{self.identificacion_cliente_oferente} / "
            f"{self.identificacion_cliente_demandante} - {self.moneda}"
        )

    def save(self, *args, **kwargs):
        # Auto-calculate contravalor if not set
        if not self.contravalor_bs and self.monto_divisa and self.tipo_cambio_bs:
            self.contravalor_bs = self.monto_divisa * self.tipo_cambio_bs
        super().save(*args, **kwargs)
