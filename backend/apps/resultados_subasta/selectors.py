from .models import ResultadoSubasta
from django.db.models import QuerySet

def list_resultados() -> QuerySet:
    return ResultadoSubasta.objects.all()

def list_pending_resultados() -> QuerySet:
    return ResultadoSubasta.objects.filter(status='pending')

def list_rejected_resultados() -> QuerySet:
    return ResultadoSubasta.objects.filter(status='rejected')

def get_resultado_by_id(resultado_id: int) -> ResultadoSubasta:
    return ResultadoSubasta.objects.filter(id=resultado_id).first()

def get_resultados_by_subasta(codigo_subasta: str) -> QuerySet:
    return ResultadoSubasta.objects.filter(codigo_identificacion_subasta=codigo_subasta)
