import logging
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime

from django.db import transaction as db_transaction
from django.conf import settings

from .models import ResultadoSubasta
from .serializers import ResultadoSubastaInput
from .sudeban_schemas import ResultadoSudebanRequestSchema, ResultadoSudebanSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import format_date_for_sudeban, format_amount

logger = logging.getLogger(__name__)

def create_resultado(data: ResultadoSubastaInput) -> ResultadoSubasta:
    """Create a new from internal data"""
    with db_transaction.atomic():
        # Calculamos contravalor
        contravalor = data.contravalor_final_bs
        if not contravalor and data.monto_final_divisa and data.tipo_cambio_final_bs:
            contravalor = data.monto_final_divisa * data.tipo_cambio_final_bs

        resultado = ResultadoSubasta.objects.create(
            codigo_ente_supervisado=data.codigo_ente_supervisado,
            fecha_recepcion_fondos=data.fecha_recepcion_fondos,
            fecha_subasta=data.fecha_subasta,
            codigo_identificacion_subasta=data.codigo_identificacion_subasta,
            tipo_operacion=data.tipo_operacion,
            estatus_solicitud_cliente=data.estatus_solicitud_cliente,
            fecha_solicitud_cliente=data.fecha_solicitud_cliente,
            moneda=data.moneda,
            identificacion_cliente=data.identificacion_cliente.upper(),
            nombre_cliente=data.nombre_cliente,
            actividad_economica_cliente=data.actividad_economica_cliente,
            monto_final_divisa=data.monto_final_divisa,
            tipo_cambio_final_bs=data.tipo_cambio_final_bs,
            contravalor_final_bs=contravalor,
            codigo_cuenta_moneda_nacional=data.codigo_cuenta_moneda_nacional,
            tipo_cuenta_moneda_nacional=data.tipo_cuenta_moneda_nacional,
            codigo_cuenta_moneda_extranjera=data.codigo_cuenta_moneda_extranjera,
            tipo_cuenta_moneda_extranjera=data.tipo_cuenta_moneda_extranjera,
            destino_fondos=data.destino_fondos,
            medio_pago=data.medio_pago,
        )

        logger.info(f"Created resultado subasta: {resultado.codigo_identificacion_subasta}")
        return resultado


def prepare_for_sudeban(resultado: ResultadoSubasta) -> ResultadoSudebanSchema:
    return ResultadoSudebanSchema(
        fechaRecepcionFondos=format_date_for_sudeban(resultado.fecha_recepcion_fondos),
        fechaSubasta=format_date_for_sudeban(resultado.fecha_subasta),
        codigoSubasta=resultado.codigo_identificacion_subasta,
        idTipoOperacion=resultado.tipo_operacion,
        estatusSolicitudCliente=resultado.estatus_solicitud_cliente,
        fechaSolicitudCliente=format_date_for_sudeban(resultado.fecha_solicitud_cliente),
        idMoneda=resultado.moneda,
        montoFinalDivisa=format_amount(resultado.monto_final_divisa, 4),
        tasaCambioFinalBs=format_amount(resultado.tipo_cambio_final_bs, 4),
        contravalorFinalBs=format_amount(resultado.contravalor_final_bs, 4),
        rifCiCliente=resultado.identificacion_cliente,
        nombreCliente=resultado.nombre_cliente,
        idActEconomicaCliente=resultado.actividad_economica_cliente,
        nroCtaBancariaCliente=resultado.codigo_cuenta_moneda_nacional,
        idTipoCtaBancariaCliente=resultado.tipo_cuenta_moneda_nacional,
        nroCtaBancariaExtCliente=resultado.codigo_cuenta_moneda_extranjera,
        idTipoCtaBancariaExtCliente=resultado.tipo_cuenta_moneda_extranjera,
        idDestinoFondos=resultado.destino_fondos,
        idMedioPago=resultado.medio_pago,
    )


def send_to_sudeban(resultados: List[ResultadoSubasta]) -> Dict[str, Any]:
    if not resultados:
        return {'success': True, 'message': 'No requests to send'}

    client = SudebanAPIClient(
        base_url=settings.SUDEBAN_API_URL,
        username=settings.SUDEBAN_USERNAME,
        password=settings.SUDEBAN_PASSWORD,
        verify_ssl=not settings.DEBUG
    )

    ente_code = resultados[0].codigo_ente_supervisado
    batch = ResultadoSudebanRequestSchema(
        idEntidadBancaria=ente_code,
        transacciones=[prepare_for_sudeban(r) for r in resultados],
    )

    # API-03 endpoint might be 'resultados-subasta-privada'
    result = client.send_transaction(
        'api-03/resultados-subasta', 
        batch.dict()
    )

    if result['success']:
        with db_transaction.atomic():
            for r in resultados:
                r.status = 'sent'
                r.last_sent_at = datetime.now()
                r.save()

        return {
            'success': True,
            'count': len(resultados),
            'response': result.get('data')
        }
    else:
        with db_transaction.atomic():
            for r in resultados:
                r.status = 'failed'
                r.retry_count += 1
                r.error_detail = result.get('detail')
                r.save()

        return {
            'success': False,
            'error': result.get('error'),
            'detail': result.get('detail')
        }
