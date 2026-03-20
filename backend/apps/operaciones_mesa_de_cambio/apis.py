from datetime import datetime
from django.conf import settings
from ninja import NinjaAPI
from typing import List

from .serializers import (
    OperacionMesaDeCambioInput,
    OperacionMesaDeCambioBatchInput,
    OperacionMesaDeCambioOutput,
    OperacionMesaDeCambioCorreccionInput,
)
from . import services, selectors
from apps.core.utils import build_error_response

api = NinjaAPI(urls_namespace='mesa_de_cambio')


@api.post("/operaciones/create", response={201: OperacionMesaDeCambioOutput, 400: dict})
def create_operacion(request, payload: OperacionMesaDeCambioInput):
    """Create a new mesa de cambio transaction."""
    try:
        operacion = services.create_operacion(payload)
        return 201, operacion
    except ValueError as e:
        return 400, build_error_response(400, str(e))
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")


@api.post("/operaciones/batch", response={201: dict, 400: dict})
def create_batch_operaciones(request, payload: OperacionMesaDeCambioBatchInput):
    """Create multiple mesa de cambio transactions in batch."""
    results = {
        'success': [],
        'errors': [],
    }

    for op_data in payload.transacciones:
        try:
            op = services.create_operacion(op_data)
            results['success'].append({'id': op.id})
        except Exception as e:
            results['errors'].append({
                'oferente': op_data.identificacion_cliente_oferente,
                'demandante': op_data.identificacion_cliente_demandante,
                'error': str(e),
            })

    return 201, results


@api.get("/operaciones/", response=List[OperacionMesaDeCambioOutput])
def list_operaciones(request, status: str = None, limit: int = 100):
    """List mesa de cambio transactions with optional status filter."""
    queryset = selectors.list_pending_operaciones()
    if status:
        queryset = queryset.filter(status=status)
    return queryset[:limit]


@api.get("/operaciones/rejected/", response=List[OperacionMesaDeCambioOutput])
def list_rejected(request):
    """List rejected mesa de cambio transactions."""
    return selectors.list_rejected_operaciones()


@api.get("/operaciones/{operacion_id}", response=OperacionMesaDeCambioOutput)
def get_operacion(request, operacion_id: int):
    """Get a single mesa de cambio transaction by ID."""
    operacion = selectors.get_operacion_by_id(operacion_id)
    if not operacion:
        return 404, {"error": "Transaction not found"}
    return operacion


@api.post("/operaciones/{operacion_id}/correct")
def correct_operacion(request, operacion_id: int, payload: OperacionMesaDeCambioCorreccionInput):
    """Correct a rejected mesa de cambio transaction."""
    try:
        operacion = services.correct_operacion(operacion_id, payload)
        return {"success": True, "id": operacion.id}
    except ValueError as e:
        message = str(e)
        status_code = 404 if 'not found' in message.lower() else 400
        return status_code, {"error": message}


@api.get("/stats/")
def get_stats(request):
    """Get mesa de cambio statistics."""
    return selectors.get_stats()


@api.post("/operaciones/send-pending", response={200: dict, 400: dict})
def send_pending_operaciones(request):
    """Manual send: transmit all pending mesa de cambio operaciones to SUDEBAN."""
    try:
        result = services.send_pending_operaciones(
            webhook_url=getattr(settings, 'SUDEBAN_WEBHOOK_URL', None)
        )
        return 200, result
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")
