import json
from datetime import datetime, timedelta
from django.http import JsonResponse
from ninja import NinjaAPI
from typing import List

from .serializers import (
    SubastaSolicitudInput,
    SubastaBatchInput,
    SubastaSolicitudOutput,
    SubastaCorreccionInput
)
from . import services, selectors
from apps.core.utils import build_error_response

api = NinjaAPI(urls_namespace='subasta')


@api.post("/solicitudes/create", response={201: SubastaSolicitudOutput, 400: dict})
def create_solicitud(request, payload: SubastaSolicitudInput):
    """Create a new subasta request"""
    try:
        solicitud = services.create_solicitud(payload)
        return 201, solicitud
    except ValueError as e:
        return 400, build_error_response(400, str(e))
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")


@api.post("/solicitudes/batch", response={201: dict, 400: dict})
def create_batch_solicitudes(request, payload: SubastaBatchInput):
    """Create multiple subasta requests in batch"""
    results = {
        'success': [],
        'errors': []
    }
    
    for solicitud_data in payload.transacciones:
        try:
            solicitud = services.create_solicitud(solicitud_data)
            results['success'].append({
                'id': solicitud.id,
                'codigo': solicitud.codigo_identificacion_subasta
            })
        except Exception as e:
            results['errors'].append({
                'codigo': solicitud_data.codigo_identificacion_subasta,
                'error': str(e)
            })
    
    return 201, results


@api.get("/solicitudes/", response=List[SubastaSolicitudOutput])
def list_solicitudes(request, status: str = None, limit: int = 100):
    """List subasta requests with optional status filter"""
    queryset = selectors.list_pending_solicitudes()
    if status:
        queryset = queryset.filter(status=status)
    return queryset[:limit]


@api.get("/solicitudes/rejected/", response=List[SubastaSolicitudOutput])
def list_rejected(request):
    """List rejected subasta requests"""
    return selectors.list_rejected_solicitudes()


@api.get("/solicitudes/{solicitud_id}", response=SubastaSolicitudOutput)
def get_solicitud(request, solicitud_id: int):
    """Get single subasta request by ID"""
    solicitud = selectors.get_solicitud_by_id(solicitud_id)
    if not solicitud:
        return 404, {"error": "Solicitud not found"}
    return solicitud


@api.get("/solicitudes/by-subasta/{codigo_subasta}", response=List[SubastaSolicitudOutput])
def get_by_subasta(request, codigo_subasta: str):
    """Get all requests for a specific subasta"""
    return selectors.get_solicitudes_by_subasta(codigo_subasta)


@api.post("/solicitudes/{solicitud_id}/correct")
def correct_solicitud(request, solicitud_id: int, payload: SubastaCorreccionInput):
    """Correct a rejected subasta request"""
    try:
        solicitud = services.correct_solicitud(solicitud_id, payload)
        return {"success": True, "id": solicitud.id}
    except ValueError as e:
        return 400, {"error": str(e)}
    except Exception as e:
        return 400, {"error": str(e)}


@api.get("/stats/")
def get_stats(request):
    """Get subasta statistics"""
    return selectors.get_stats()


@api.get("/summary/")
def get_summary(request, fecha_inicio: str = None, fecha_fin: str = None):
    """Get subasta summary for date range"""
    try:
        if fecha_inicio and fecha_fin:
            inicio = datetime.fromisoformat(fecha_inicio)
            fin = datetime.fromisoformat(fecha_fin)
        else:
            # Default to last 30 days
            fin = datetime.now()
            inicio = fin - timedelta(days=30)
        
        return selectors.get_subasta_summary(inicio, fin)
    except Exception as e:
        return 400, {"error": str(e)}


@api.post("/callback/")
def sudeban_callback(request):
    """
    Webhook endpoint for SUDEBAN callbacks
    """
    try:
        data = request.POST or json.loads(request.body)
        codigo_subasta = data.get('codigoSubasta')
        status = data.get('status')
        error_code = data.get('errorCode')
        
        if not codigo_subasta or not status:
            return 400, {"error": "Missing required fields"}
        
        services.process_sudeban_callback(codigo_subasta, status, error_code)
        return {"success": True}
    except Exception as e:
        return 400, {"error": str(e)}