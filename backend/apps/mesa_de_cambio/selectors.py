from django.db.models import QuerySet, Sum
from .models import MesaDeCambioOperacion
from datetime import datetime, timedelta
from typing import Optional, List


def get_operacion_by_id(operacion_id: int) -> Optional[MesaDeCambioOperacion]:
    """Get single operation by ID"""
    try:
        return MesaDeCambioOperacion.objects.get(id=operacion_id)
    except MesaDeCambioOperacion.DoesNotExist:
        return None


def get_operacion_by_codigo(codigo: str) -> Optional[MesaDeCambioOperacion]:
    """Get operation by identification code"""
    try:
        return MesaDeCambioOperacion.objects.get(codigo_identificacion_operacion=codigo)
    except MesaDeCambioOperacion.DoesNotExist:
        return None


def list_operaciones(status_filter: List[str] = None) -> QuerySet:
    """List operations with optional status filter"""
    if status_filter is None:
        status_filter = ['pending', 'rejected']
    return MesaDeCambioOperacion.objects.filter(
        status__in=status_filter
    ).order_by('fecha_operacion')


def list_operaciones_for_batch(
    max_records: int = 1000,
    status_filter: List[str] = None
) -> QuerySet:
    """List operations ready for batch processing"""
    if status_filter is None:
        status_filter = ['pending', 'rejected']
    return MesaDeCambioOperacion.objects.filter(
        status__in=status_filter,
        retry_count__lt=5
    ).order_by('fecha_operacion')[:max_records]


def list_rejected_operaciones() -> QuerySet:
    """List all rejected operations"""
    return MesaDeCambioOperacion.objects.filter(
        status='rejected'
    ).order_by('-updated_at')


def get_stats() -> dict:
    """Get statistics for dashboard"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)

    base_qs = MesaDeCambioOperacion.objects.all()

    return {
        'total': base_qs.count(),
        'pending': base_qs.filter(status='pending').count(),
        'success': base_qs.filter(status='success').count(),
        'rejected': base_qs.filter(status='rejected').count(),
        'today': base_qs.filter(created_at__gte=today_start).count(),
        'week': base_qs.filter(created_at__gte=week_ago).count(),
        'total_amount': base_qs.filter(status='success').aggregate(
            total=Sum('monto_divisa')
        )['total'] or 0,
    }
