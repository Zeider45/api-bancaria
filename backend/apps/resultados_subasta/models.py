from django.db import models
from apps.core.models import BaseModel, TransactionStatus

class ResultadoSubasta(BaseModel):
    """
    Model for API-03 Resultados de la Subasta Privada
    Based on SIB-MET-API-03 manual
    """

    # Subasta data (DATOS SUBASTA PRIVADA)
    codigo_ente_supervisado = models.CharField(
        max_length=4,
        help_text="Código comercial asignado por BCV"
    )
    fecha_recepcion_fondos = models.DateTimeField(
        help_text="Fecha en la que el Ente recibió los fondos del BCV (AAAA-MM-DDTHH:MM:SS.sss)"
    )
    fecha_subasta = models.DateTimeField(
        help_text="Fecha en la que se realizó la subasta privada (AAAA-MM-DDTHH:MM:SS.sss)"
    )
    codigo_identificacion_subasta = models.CharField(
        max_length=50,
        help_text="Código que identifica la subasta privada según BCV"
    )

    # Resultados data (DE LOS RESULTADOS)
    tipo_operacion = models.IntegerField(
        help_text="Código tipo operación (8 o 9)"
    )
    estatus_solicitud_cliente = models.CharField(
        max_length=3,
        help_text="SA (Solicitud Aprobada) o SNA (Solicitud No Aprobada)"
    )
    
    # Detalle resultados
    fecha_solicitud_cliente = models.DateTimeField(
        help_text="Día hábil en el que el cliente realizó la solicitud"
    )
    moneda = models.IntegerField(
        help_text="Código del tipo de moneda (Distinto a 928)"
    )
    monto_final_divisa = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text="Monto final en moneda extranjera"
    )
    tipo_cambio_final_bs = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text="Tipo de cambio final en Bolívares"
    )
    contravalor_final_bs = models.DecimalField(
        max_digits=20,
        decimal_places=4,
        help_text="Contravalor final en Bolívares (Monto * Tipo Cambio)"
    )

    # Identificación cliente y cuentas
    identificacion_cliente = models.CharField(
        max_length=20,
        help_text="RIF o identificación del cliente"
    )
    nombre_cliente = models.CharField(
        max_length=100,
        help_text="Nombres y apellidos o razón social"
    )
    actividad_economica_cliente = models.CharField(
        max_length=10,
        help_text="Código de actividad económica del cliente"
    )

    codigo_cuenta_moneda_nacional = models.CharField(
        max_length=20,
        help_text="Código de cuenta en moneda nacional"
    )
    tipo_cuenta_moneda_nacional = models.IntegerField(
        help_text="Código tipo cuenta nacional"
    )
    codigo_cuenta_moneda_extranjera = models.CharField(
        max_length=20,
        help_text="Código de cuenta en moneda extranjera"
    )
    tipo_cuenta_moneda_extranjera = models.IntegerField(
        help_text="Código tipo cuenta extranjera"
    )
    
    destino_fondos = models.IntegerField(
        help_text="Código destino de los fondos"
    )
    medio_pago = models.IntegerField(
        help_text="Código medio de pago"
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
        db_table = 'resultados_subasta'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['codigo_identificacion_subasta']),
            models.Index(fields=['fecha_subasta']),
        ]
        verbose_name = 'Resultado de Subasta'
        verbose_name_plural = 'Resultados de Subasta'

    def __str__(self):
        return f"{self.codigo_identificacion_subasta} - {self.identificacion_cliente} - {self.estatus_solicitud_cliente}"

    def save(self, *args, **kwargs):
        if not self.contravalor_final_bs and self.monto_final_divisa and self.tipo_cambio_final_bs:
            self.contravalor_final_bs = self.monto_final_divisa * self.tipo_cambio_final_bs
        super().save(*args, **kwargs)
