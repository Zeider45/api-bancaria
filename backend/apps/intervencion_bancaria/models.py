from django.db import models
from apps.core.models import BaseModel, TransactionStatus, ClientType
from decimal import Decimal


class IntervencionTransaccion(BaseModel):
    """
    Model for API-01 Intervención Cambiaria transactions
    """
    
    # Intervention data
    codigo_operacion = models.CharField(
        max_length=40,
        default='',
        blank=True,
        help_text="Código de identificación único de la operación (API-01)"
    )
    codigo_ente_supervisado = models.CharField(max_length=4)
    tipo_intervencion = models.CharField(max_length=10)  # 1, 3, 7, etc.
    fecha_intervencion = models.DateTimeField()
    codigo_identificacion_intervencion = models.CharField(max_length=10, unique=True)
    
    # Transaction data
    fecha_operacion_cliente = models.DateTimeField()
    moneda = models.IntegerField()  # 840 = USD
    identificacion_cliente = models.CharField(max_length=20)  # RIF
    nombre_cliente = models.CharField(max_length=100)
    actividad_economica_cliente = models.CharField(max_length=10)
    monto_divisa = models.DecimalField(max_digits=20, decimal_places=4)
    tipo_cambio_bs = models.DecimalField(max_digits=20, decimal_places=4)
    contravalor_bs = models.DecimalField(max_digits=20, decimal_places=4)
    
    # Cuentas
    codigo_cuenta_moneda_nacional = models.CharField(max_length=20, default='0')
    tipo_cuenta_moneda_nacional = models.IntegerField(default=0)  # 8, 9, 10 or 0
    codigo_cuenta_moneda_extranjera = models.CharField(max_length=20, default='0')
    tipo_cuenta_moneda_extranjera = models.IntegerField(default=0)  # 31, 32 or 0
    
    destino_fondos = models.IntegerField()  # T006
    medio_pago = models.IntegerField()  # T007
    
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
        db_table = 'intervencion_transacciones'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fecha_operacion_cliente']),
            models.Index(fields=['codigo_identificacion_intervencion']),
        ]
    
    def __str__(self):
        return f"{self.codigo_identificacion_intervencion} - {self.nombre_cliente}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate contravalor if not set
        if not self.contravalor_bs and self.monto_divisa and self.tipo_cambio_bs:
            self.contravalor_bs = self.monto_divisa * self.tipo_cambio_bs
        super().save(*args, **kwargs)