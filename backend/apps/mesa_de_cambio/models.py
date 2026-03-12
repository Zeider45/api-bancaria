from django.db import models
from apps.core.models import BaseModel, TransactionStatus
from decimal import Decimal


class MesaDeCambioOperacion(BaseModel):
    """
    Model for API-03 Mesa de Cambio operations
    """

    # Operation identification
    codigo_ente_supervisado = models.CharField(max_length=4)
    codigo_identificacion_operacion = models.CharField(max_length=20, unique=True)

    # Operation date
    fecha_operacion = models.DateTimeField()

    # Client data
    identificacion_cliente = models.CharField(max_length=20)
    nombre_cliente = models.CharField(max_length=100)
    actividad_economica_cliente = models.CharField(max_length=10)

    # Currency and amounts
    moneda = models.IntegerField()
    monto_divisa = models.DecimalField(max_digits=20, decimal_places=4)
    tipo_cambio_bs = models.DecimalField(max_digits=20, decimal_places=4)
    contravalor_bs = models.DecimalField(max_digits=20, decimal_places=4)

    # Accounts
    codigo_cuenta_moneda_nacional = models.CharField(max_length=20, default='0')
    tipo_cuenta_moneda_nacional = models.IntegerField(default=0)
    codigo_cuenta_moneda_extranjera = models.CharField(max_length=20, default='0')
    tipo_cuenta_moneda_extranjera = models.IntegerField(default=0)

    destino_fondos = models.IntegerField()
    medio_pago = models.IntegerField()

    # System fields
    status = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.PENDING
    )
    external_id = models.CharField(max_length=100, null=True, blank=True)
    error_code = models.IntegerField(null=True, blank=True)
    error_detail = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    last_sent_at = models.DateTimeField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'mesa_de_cambio_operaciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fecha_operacion']),
            models.Index(fields=['codigo_identificacion_operacion']),
        ]

    def __str__(self):
        return f"{self.codigo_identificacion_operacion} - {self.nombre_cliente}"

    def save(self, *args, **kwargs):
        if not self.contravalor_bs and self.monto_divisa and self.tipo_cambio_bs:
            self.contravalor_bs = self.monto_divisa * self.tipo_cambio_bs
        super().save(*args, **kwargs)
