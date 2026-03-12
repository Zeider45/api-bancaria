from ninja import NinjaAPI
from typing import List

from .serializers import (
    MesaDeCambioOperacionInput,
    MesaDeCambioBatchInput,
    MesaDeCambioOperacionOutput,
    MesaDeCambioCorreccionInput,
)
from . import services, selectors
from apps.core.utils import build_error_response

api = NinjaAPI(urls_namespace='mesa_de_cambio')


@api.post("/operaciones/create", response={201: MesaDeCambioOperacionOutput, 400: dict})
def create_operacion(request, payload: MesaDeCambioOperacionInput):
    """Create a new mesa de cambio operation"""
    try:
        operacion = services.create_operacion(payload)
        return 201, operacion
    except ValueError as e:
        return 400, build_error_response(400, str(e))
    except Exception as e:
        return 400, build_error_response(400, f"Error interno: {str(e)}")


@api.post("/operaciones/batch", response={201: dict, 400: dict})
def create_batch_operaciones(request, payload: MesaDeCambioBatchInput):
    """Create multiple operations in batch"""
    results = {
        'success': [],
        'errors': []
    }

    for op_data in payload.operaciones:
        try:
            op = services.create_operacion(op_data)
            results['success'].append({
                'id': op.id,
                'codigo': op.codigo_identificacion_operacion
            })
        except Exception as e:
            results['errors'].append({
                'codigo': op_data.codigo_identificacion_operacion,
                'error': str(e)
            })

    return 201, results


@api.get("/operaciones/", response=List[MesaDeCambioOperacionOutput])
def list_operaciones(request, status: str = None, limit: int = 100):
    """List operations with optional status filter"""
    if status:
        queryset = selectors.list_operaciones(status_filter=[status])
    else:
        queryset = selectors.list_operaciones()
    return queryset[:limit]


@api.get("/operaciones/rejected/", response=List[MesaDeCambioOperacionOutput])
def list_rejected(request):
    """List rejected operations"""
    return selectors.list_rejected_operaciones()


@api.get("/operaciones/{operacion_id}", response={200: MesaDeCambioOperacionOutput, 404: dict})
def get_operacion(request, operacion_id: int):
    """Get single operation by ID"""
    operacion = selectors.get_operacion_by_id(operacion_id)
    if not operacion:
        return 404, {"error": "Operation not found"}
    return operacion


@api.post("/operaciones/{operacion_id}/correct", response={200: dict, 400: dict, 404: dict})
def correct_operacion(request, operacion_id: int, payload: MesaDeCambioCorreccionInput):
    """Correct a rejected operation"""
    try:
        operacion = services.correct_operacion(operacion_id, payload)
        return {"success": True, "id": operacion.id}
    except ValueError as e:
        message = str(e)
        status_code = 404 if 'not found' in message.lower() else 400
        return status_code, {"error": message}


@api.get("/stats/")
def get_stats(request):
    """Get mesa de cambio statistics"""
    return selectors.get_stats()
