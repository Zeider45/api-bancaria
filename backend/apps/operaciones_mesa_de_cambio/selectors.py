from django.db.models import QuerySet
from .models import OperacionMesaDeCambio
from django.utils import timezone
from typing import Optional, List


def get_operacion_by_id(operacion_id: int) -> Optional[OperacionMesaDeCambio]:
    """Get a single mesa de cambio transaction by ID."""
    try:
        return OperacionMesaDeCambio.objects.get(id=operacion_id)
    except OperacionMesaDeCambio.DoesNotExist:
        return None


def list_pending_operaciones() -> QuerySet:
    """List all pending or rejected mesa de cambio transactions."""
    return OperacionMesaDeCambio.objects.filter(
        status__in=['pending', 'rejected']
    ).order_by('fecha_pacto')


def list_operaciones_for_batch(
    max_records: int = 1000,
    status_filter: List[str] = None,
) -> QuerySet:
    """List transactions ready for batch processing (max 5 retries)."""
    if status_filter is None:
        status_filter = ['pending', 'rejected']

    return OperacionMesaDeCambio.objects.filter(
        status__in=status_filter,
        retry_count__lt=5,
    ).order_by('fecha_pacto')[:max_records]


def list_rejected_operaciones() -> QuerySet:
    """List all rejected mesa de cambio transactions."""
    return OperacionMesaDeCambio.objects.filter(
        status='rejected'
    ).order_by('-updated_at')


def get_stats() -> dict:
    """Get statistics for dashboard."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    return {
        'total': OperacionMesaDeCambio.objects.count(),
        'pending': OperacionMesaDeCambio.objects.filter(status='pending').count(),
        'sent': OperacionMesaDeCambio.objects.filter(status='sent').count(),
        'success': OperacionMesaDeCambio.objects.filter(status='success').count(),
        'rejected': OperacionMesaDeCambio.objects.filter(status='rejected').count(),
        'failed': OperacionMesaDeCambio.objects.filter(status='failed').count(),
        'today': OperacionMesaDeCambio.objects.filter(created_at__gte=today_start).count(),
    }
