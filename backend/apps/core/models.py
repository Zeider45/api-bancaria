from django.db import models
from django.utils import timezone

class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating 
    created and modified fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel):
    """
    Abstract base model with soft delete functionality.
    """
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def soft_delete(self):
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    class Meta:
        abstract = True


class CatalogBaseModel(BaseModel):
    """Base model for reusable lookup tables stored in the database."""
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    sort_order = models.PositiveIntegerField(default=0)
    is_selectable = models.BooleanField(default=True)

    class Meta:
        abstract = True
        ordering = ['sort_order', 'code']

    def __str__(self):
        return f"{self.code} - {self.name}"


class EnteSupervisadoCatalog(CatalogBaseModel):
    code = models.CharField(max_length=4, unique=True)
    name = models.CharField(max_length=200)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_entes_supervisados_catalog'
        verbose_name = 'Ente supervisado'
        verbose_name_plural = 'Entes supervisados'


class MecanismoCambiarioCatalog(CatalogBaseModel):
    code = models.CharField(max_length=2, unique=True)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_mecanismos_cambiarios_catalog'
        verbose_name = 'Mecanismo cambiario'
        verbose_name_plural = 'Mecanismos cambiarios'


class MonedaCatalog(CatalogBaseModel):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=10)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_monedas_catalog'
        verbose_name = 'Moneda'
        verbose_name_plural = 'Monedas'


class ActividadEconomicaCatalog(CatalogBaseModel):
    code = models.CharField(max_length=4, unique=True)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_actividades_economicas_catalog'
        verbose_name = 'Actividad económica'
        verbose_name_plural = 'Actividades económicas'


class InstrumentoCaptacionCatalog(CatalogBaseModel):
    code = models.CharField(max_length=2, unique=True)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_instrumentos_captacion_catalog'
        verbose_name = 'Instrumento de captación'
        verbose_name_plural = 'Instrumentos de captación'


class DestinoFondosCatalog(CatalogBaseModel):
    code = models.CharField(max_length=2, unique=True)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_destinos_fondos_catalog'
        verbose_name = 'Destino de los fondos'
        verbose_name_plural = 'Destinos de los fondos'


class MedioPagoCatalog(CatalogBaseModel):
    code = models.CharField(max_length=2, unique=True)

    class Meta(CatalogBaseModel.Meta):
        db_table = 'core_medios_pago_catalog'
        verbose_name = 'Medio de pago'
        verbose_name_plural = 'Medios de pago'


class TransactionStatus(models.TextChoices):
    """Status options for all transactions"""
    PENDING = 'pending', 'Pendiente'
    SENT = 'sent', 'Enviado'
    SUCCESS = 'success', 'Exitoso'
    REJECTED = 'rejected', 'Rechazado'
    CORRECTED = 'corrected', 'Corregido'
    FAILED = 'failed', 'Fallido'


class ClientType(models.TextChoices):
    """Venezuelan RIF types"""
    VENEZUELAN = 'V', 'Venezolano'
    FOREIGN = 'E', 'Extranjero'
    COMPANY = 'J', 'Jurídico'
    GOVERNMENT = 'G', 'Gobierno'
    COMMUNITY = 'C', 'Comuna y Consejos Comunales'
    PERSONAL_REGISTRY = 'R', 'Registro de Firma Personal'