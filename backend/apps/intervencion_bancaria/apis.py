from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from ninja import NinjaAPI
from typing import List

from .serializers import (
    IntervencionTransaccionInput, 
    IntervencionBatchInput,
    IntervencionTransaccionOutput,
    IntervencionCorreccionInput
)
from . import services, selectors
from apps.core.utils import build_error_response, decode_sudeban_error

api = NinjaAPI(urls_namespace='intervencion')


@api.post("/transacciones/create", response={201: IntervencionTransaccionOutput, 400: dict})
def create_transaccion(request, payload: IntervencionTransaccionInput):
    """Create a new intervencion transaction"""
    try:
        transaccion = services.create_transaccion(payload)
        return 201, transaccion
    except ValueError as e:
        return 400, build_error_response(400, str(e))
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")


@api.post("/transacciones/batch", response={201: dict, 400: dict})
def create_batch_transacciones(request, payload: IntervencionBatchInput):
    """Create multiple transactions in batch"""
    results = {
        'success': [],
        'errors': []
    }
    
    for trans_data in payload.transacciones:
        try:
            trans = services.create_transaccion(trans_data)
            results['success'].append({
                'id': trans.id,
                'codigo': trans.codigo_identificacion_intervencion
            })
        except Exception as e:
            results['errors'].append({
                'codigo': trans_data.codigo_identificacion_intervencion,
                'error': str(e)
            })
    
    return 201, results


@api.get("/transacciones/", response=List[IntervencionTransaccionOutput])
def list_transacciones(request, status: str = None, limit: int = 100):
    """List transactions with optional status filter"""
    queryset = selectors.list_pending_transacciones()
    if status:
        queryset = queryset.filter(status=status)
    return queryset[:limit]


@api.get("/transacciones/rejected/", response=List[IntervencionTransaccionOutput])
def list_rejected(request):
    """List rejected transactions"""
    return selectors.list_rejected_transacciones()


@api.get("/transacciones/{transaccion_id}", response=IntervencionTransaccionOutput)
def get_transaccion(request, transaccion_id: int):
    """Get single transaction by ID"""
    transaccion = selectors.get_transaccion_by_id(transaccion_id)
    if not transaccion:
        return 404, {"error": "Transaction not found"}
    return transaccion


@api.post("/transacciones/{transaccion_id}/correct")
def correct_transaccion(request, transaccion_id: int, payload: IntervencionCorreccionInput):
    """Correct a rejected transaction"""
    try:
        transaccion = services.correct_transaccion(transaccion_id, payload)
        return {"success": True, "id": transaccion.id}
    except ValueError as e:
        message = str(e)
        status_code = 404 if 'not found' in message.lower() else 400
        return status_code, {"error": message}


@api.get("/stats/")
def get_stats(request):
    """Get intervention statistics"""
    return selectors.get_stats()


@api.post("/transacciones/send-pending", response={200: dict, 400: dict})
def send_pending_transacciones(request):
    """Manual send: transmit all pending intervencion transacciones to SUDEBAN."""
    try:
        result = services.send_pending_transacciones(
            webhook_url=getattr(settings, 'SUDEBAN_WEBHOOK_URL', None)
        )
        return 200, result
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")