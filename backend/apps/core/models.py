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