import json
from ninja import NinjaAPI
from typing import List

from .serializers import (
    ResultadoSubastaInput,
    ResultadoBatchInput,
    ResultadoSubastaOutput
)
from . import services, selectors
from apps.core.utils import build_error_response

api = NinjaAPI(urls_namespace='resultados_subasta')

@api.post("/create", response={201: ResultadoSubastaOutput, 400: dict})
def create_resultado(request, payload: ResultadoSubastaInput):
    """Create a new resultado subasta"""
    try:
        resultado = services.create_resultado(payload)
        return 201, resultado
    except ValueError as e:
        return 400, build_error_response(400, str(e))
    except Exception as e:
        return 400, build_error_response(500, f"Error interno: {str(e)}")

@api.post("/batch", response={201: dict, 400: dict})
def create_batch_resultados(request, payload: ResultadoBatchInput):
    """Create multiple resultado subasta requests in batch"""
    results = {
        'success': [],
        'errors': []
    }

    for resultado_data in payload.transacciones:
        try:
            resultado = services.create_resultado(resultado_data)
            results['success'].append({
                'id': resultado.id,
                'codigo': resultado.codigo_identificacion_subasta
            })
        except Exception as e:
            results['errors'].append({
                'codigo': resultado_data.codigo_identificacion_subasta,
                'error': str(e)
            })

    return 201, results

@api.get("/", response=List[ResultadoSubastaOutput])
def list_resultados(request, status: str = None, limit: int = 100):
    queryset = selectors.list_resultados()
    if status:
        queryset = queryset.filter(status=status)
    return queryset[:limit]

@api.get("/{resultado_id}", response=ResultadoSubastaOutput)
def get_resultado(request, resultado_id: int):
    resultado = selectors.get_resultado_by_id(resultado_id)
    if not resultado:
        return 404, {"error": "Resultado not found"}
    return resultado

@api.get("/by-subasta/{codigo_subasta}", response=List[ResultadoSubastaOutput])
def get_by_subasta(request, codigo_subasta: str):
    return selectors.get_resultados_by_subasta(codigo_subasta)
