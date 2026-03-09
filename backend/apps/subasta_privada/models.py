from django.db import models
from apps.core.models import BaseModel, TransactionStatus


class SubastaSolicitud(BaseModel):
    """
    Model for API-02 Subasta Privada requests
    Based on SIB-MET-API-02 manual
    """
    
    # Subasta data (DATOS SUBASTA PRIVADA)
    codigo_ente_supervisado = models.CharField(
        max_length=4,
        help_text="Código comercial asignado por BCV"
    )
    fecha_subasta = models.DateTimeField(
        help_text="Fecha en la que se realiza la subasta privada"
    )
    codigo_identificacion_subasta = models.CharField(
        max_length=50,
        unique=True,
        help_text="Código que identifica la subasta privada según BCV"
    )
    
    # Solicitud data (DATOS DE LA SOLICITUD)
    fecha_solicitud_cliente = models.DateTimeField(
        help_text="Día hábil bancario que el cliente realizó la solicitud"
    )
    moneda = models.IntegerField(
        help_text="Código del tipo de moneda (T003. Moneda)"
    )
    identificacion_cliente = models.CharField(
        max_length=20,
        help_text="RIF o identificación del cliente (prefijo + número)"
    )
    nombre_cliente = models.CharField(
        max_length=100,
        help_text="Nombres y apellidos o razón social"
    )
    actividad_economica_cliente = models.CharField(
        max_length=10,
        help_text="Código de actividad económica (T004)"
    )
    monto_divisa = models.DecimalField(
        max_digits=20, 
        decimal_places=4,
        help_text="Monto en moneda extranjera solicitado"
    )
    tipo_cambio_bs = models.DecimalField(
        max_digits=20, 
        decimal_places=4,
        help_text="Tipo de cambio en Bolívares de la solicitud"
    )
    contravalor_bs = models.DecimalField(
        max_digits=20, 
        decimal_places=4,
        help_text="Monto * Tipo Cambio"
    )
    
    # Cuentas
    codigo_cuenta_moneda_nacional = models.CharField(
        max_length=20,
        help_text="Código de cuenta en moneda nacional (20 dígitos)"
    )
    tipo_cuenta_moneda_nacional = models.IntegerField(
        help_text="Código tipo cuenta nacional (T005: 8,9,10)"
    )
    codigo_cuenta_moneda_extranjera = models.CharField(
        max_length=20,
        help_text="Código de cuenta en moneda extranjera (20 dígitos)"
    )
    tipo_cuenta_moneda_extranjera = models.IntegerField(
        help_text="Código tipo cuenta extranjera (T005: 31,32)"
    )
    
    destino_fondos = models.IntegerField(
        help_text="Código destino de los fondos (T006)"
    )
    medio_pago = models.IntegerField(
        help_text="Código medio de pago (T007) - Debe ser 2 para subasta"
    )
    
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
        db_table = 'subasta_solicitudes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['fecha_solicitud_cliente']),
            models.Index(fields=['codigo_identificacion_subasta']),
            models.Index(fields=['fecha_subasta']),
        ]
        verbose_name = 'Solicitud de Subasta'
        verbose_name_plural = 'Solicitudes de Subasta'
    
    def __str__(self):
        return f"{self.codigo_identificacion_subasta} - {self.nombre_cliente}"
    
    def save(self, *args, **kwargs):
        # Auto-calculate contravalor if not set
        if not self.contravalor_bs and self.monto_divisa and self.tipo_cambio_bs:
            self.contravalor_bs = self.monto_divisa * self.tipo_cambio_bs
        super().save(*args, **kwargs)