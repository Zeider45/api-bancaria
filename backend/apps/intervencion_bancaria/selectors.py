from django.db.models import QuerySet
from .models import IntervencionTransaccion
from datetime import datetime, timedelta
from typing import Optional, List


def get_transaccion_by_id(transaccion_id: int) -> Optional[IntervencionTransaccion]:
    """Get single transaction by ID"""
    try:
        return IntervencionTransaccion.objects.get(id=transaccion_id)
    except IntervencionTransaccion.DoesNotExist:
        return None


def get_transaccion_by_codigo(codigo: str) -> Optional[IntervencionTransaccion]:
    """Get transaction by intervention code"""
    try:
        return IntervencionTransaccion.objects.get(codigo_identificacion_intervencion=codigo)
    except IntervencionTransaccion.DoesNotExist:
        return None


def list_pending_transacciones() -> QuerySet:
    """List all pending transactions"""
    return IntervencionTransaccion.objects.filter(
        status__in=['pending', 'rejected']
    ).order_by('fecha_operacion_cliente')


def list_transacciones_for_batch(
    max_records: int = 1000,
    status_filter: List[str] = None
) -> QuerySet:
    """List transactions ready for batch processing"""
    if status_filter is None:
        status_filter = ['pending', 'rejected']
    
    return IntervencionTransaccion.objects.filter(
        status__in=status_filter,
        retry_count__lt=5  # Max 5 retries
    ).order_by('fecha_operacion_cliente')[:max_records]


def list_rejected_transacciones() -> QuerySet:
    """List all rejected transactions"""
    return IntervencionTransaccion.objects.filter(
        status='rejected'
    ).order_by('-updated_at')


def get_stats() -> dict:
    """Get statistics for dashboard"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        'total': IntervencionTransaccion.objects.count(),
        'pending': IntervencionTransaccion.objects.filter(status='pending').count(),
        'success': IntervencionTransaccion.objects.filter(status='success').count(),
        'rejected': IntervencionTransaccion.objects.filter(status='rejected').count(),
        'today': IntervencionTransaccion.objects.filter(created_at__gte=today_start).count(),
    }