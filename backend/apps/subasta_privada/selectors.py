from django.db.models import QuerySet, Count, Sum
from .models import SubastaSolicitud
from datetime import datetime, timedelta
from typing import Optional, List


def get_solicitud_by_id(solicitud_id: int) -> Optional[SubastaSolicitud]:
    """Get single subasta request by ID"""
    try:
        return SubastaSolicitud.objects.get(id=solicitud_id)
    except SubastaSolicitud.DoesNotExist:
        return None


def get_solicitud_by_codigo(codigo: str) -> Optional[SubastaSolicitud]:
    """Get subasta request by subasta code"""
    try:
        return SubastaSolicitud.objects.get(codigo_identificacion_subasta=codigo)
    except SubastaSolicitud.DoesNotExist:
        return None


def list_pending_solicitudes() -> QuerySet:
    """List all pending subasta requests"""
    return SubastaSolicitud.objects.filter(
        status__in=['pending', 'rejected']
    ).order_by('fecha_solicitud_cliente')


def list_solicitudes_for_batch(
    max_records: int = 1000,
    status_filter: List[str] = None
) -> QuerySet:
    """List subasta requests ready for batch processing"""
    if status_filter is None:
        status_filter = ['pending', 'rejected']
    
    return SubastaSolicitud.objects.filter(
        status__in=status_filter,
        retry_count__lt=5  # Max 5 retries
    ).order_by('fecha_solicitud_cliente')[:max_records]


def list_rejected_solicitudes() -> QuerySet:
    """List all rejected subasta requests"""
    return SubastaSolicitud.objects.filter(
        status='rejected'
    ).order_by('-updated_at')


def get_solicitudes_by_subasta(codigo_subasta: str) -> QuerySet:
    """Get all requests for a specific subasta"""
    return SubastaSolicitud.objects.filter(
        codigo_identificacion_subasta=codigo_subasta
    ).order_by('fecha_solicitud_cliente')


def get_stats() -> dict:
    """Get statistics for dashboard"""
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    
    base_qs = SubastaSolicitud.objects.all()
    
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


def get_subasta_summary(fecha_inicio: datetime, fecha_fin: datetime) -> dict:
    """Get summary of subastas in date range"""
    return SubastaSolicitud.objects.filter(
        fecha_subasta__range=[fecha_inicio, fecha_fin]
    ).values('fecha_subasta', 'codigo_identificacion_subasta').annotate(
        total_solicitudes=Count('id'),
        monto_total=Sum('monto_divisa')
    ).order_by('fecha_subasta')