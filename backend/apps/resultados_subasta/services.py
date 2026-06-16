import logging
import json
from collections import defaultdict
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

from django.db import transaction as db_transaction
from django.conf import settings
from django.utils import timezone

from .models import ResultadoSubasta
from .serializers import ResultadoSubastaInput
from .sudeban_schemas import ResultadoSudebanRequestSchema, ResultadoSudebanSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import (
    format_date_for_sudeban,
    format_amount,
    decode_sudeban_error,
    extract_sudeban_error_code,
    get_sudeban_ente_supervisado,
)
from apps.core.models import TransactionStatus
from apps.core import selectors as core_selectors

logger = logging.getLogger(__name__)

def create_resultado(data: ResultadoSubastaInput) -> ResultadoSubasta:
    """Create a new from internal data"""
    with db_transaction.atomic():
        # Calculamos contravalor
        contravalor = data.contravalor_final_bs
        if not contravalor and data.monto_final_divisa and data.tipo_cambio_final_bs:
            contravalor = data.monto_final_divisa * data.tipo_cambio_final_bs

        resultado = ResultadoSubasta.objects.create(
            codigo_ente_supervisado=get_sudeban_ente_supervisado(),
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


def validate_resultado_for_sudeban(resultado: ResultadoSubasta) -> Tuple[bool, List[str]]:
    """Validate API-03 business rules before sending."""

    errors: List[str] = []

    if not core_selectors.is_valid_ente_supervisado(resultado.codigo_ente_supervisado):
        errors.append('Código Ente Supervisado inválido (no existe en el catálogo)')

    if resultado.moneda == 928:
        errors.append('Moneda no puede ser Bolívar (928)')
    elif not core_selectors.is_valid_moneda(resultado.moneda):
        errors.append('Moneda inválida (no existe en el catálogo)')

    if not core_selectors.is_valid_actividad_economica(resultado.actividad_economica_cliente):
        errors.append('Actividad Económica inválida (no existe en el catálogo)')

    if resultado.tipo_cuenta_moneda_nacional not in (8, 9, 10):
        errors.append('Tipo cuenta nacional debe ser 8, 9 o 10')
    elif not core_selectors.is_valid_instrumento_captacion(resultado.tipo_cuenta_moneda_nacional):
        errors.append('Tipo cuenta nacional inválida (no existe en el catálogo)')

    if resultado.tipo_cuenta_moneda_extranjera not in (31, 32):
        errors.append('Tipo cuenta extranjera debe ser 31 o 32')
    elif not core_selectors.is_valid_instrumento_captacion(resultado.tipo_cuenta_moneda_extranjera):
        errors.append('Tipo cuenta extranjera inválida (no existe en el catálogo)')

    if resultado.tipo_operacion == 8:
        if str(resultado.codigo_identificacion_subasta) != '0':
            errors.append('Si tipo_operacion es 8, codigo_identificacion_subasta debe ser "0"')
        if resultado.estatus_solicitud_cliente != 'SA':
            errors.append('Si tipo_operacion es 8, estatus_solicitud_cliente debe ser "SA"')
        if resultado.fecha_subasta.date().isoformat() != '1900-01-01':
            errors.append('Si tipo_operacion es 8, fecha_subasta debe ser 1900-01-01')
        if resultado.fecha_solicitud_cliente.date().isoformat() != '1900-01-01':
            errors.append('Si tipo_operacion es 8, fecha_solicitud_cliente debe ser 1900-01-01')
    elif resultado.tipo_operacion == 9:
        if str(resultado.codigo_identificacion_subasta) == '0':
            errors.append('Si tipo_operacion es 9, codigo_identificacion_subasta no debe ser "0"')
        if resultado.fecha_solicitud_cliente.date() != resultado.fecha_subasta.date():
            errors.append('Si tipo_operacion es 9, fecha_solicitud_cliente debe ser igual a fecha_subasta')
    else:
        errors.append('tipo_operacion debe ser 8 o 9')

    if resultado.estatus_solicitud_cliente == 'SA':
        if resultado.monto_final_divisa <= 0:
            errors.append('Si es SA, monto_final_divisa debe ser mayor a 0')
        if resultado.tipo_cambio_final_bs <= 0:
            errors.append('Si es SA, tipo_cambio_final_bs debe ser mayor a 0')
        if resultado.destino_fondos == 0:
            errors.append('Si es SA, destino_fondos no puede ser 0')
        elif not core_selectors.is_valid_destino_fondos(resultado.destino_fondos):
            errors.append('Destino de Fondos inválido (no existe en el catálogo)')

        if resultado.medio_pago != 2:
            errors.append('Si es SA, medio_pago debe ser 2 (Transferencia)')
        elif not core_selectors.is_valid_medio_pago(resultado.medio_pago):
            errors.append('Medio de Pago inválido (no existe en el catálogo)')
    elif resultado.estatus_solicitud_cliente == 'SNA':
        if resultado.monto_final_divisa != 0:
            errors.append('Si es SNA, monto_final_divisa debe ser 0')
        if resultado.tipo_cambio_final_bs != 0:
            errors.append('Si es SNA, tipo_cambio_final_bs debe ser 0')
        if resultado.destino_fondos != 0:
            errors.append('Si es SNA, destino_fondos debe ser 0')
        if resultado.medio_pago != 0:
            errors.append('Si es SNA, medio_pago debe ser 0')
    else:
        errors.append('estatus_solicitud_cliente inválido (debe ser SA o SNA)')

    return len(errors) == 0, errors


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


def send_to_sudeban(
    resultados: List[ResultadoSubasta],
    webhook_url: Optional[str] = None,
    id_entidad_bancaria: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a batch of resultados to SUDEBAN (API-03).

    If `resultados` is empty, the function will still transmit a payload with
    `transacciones=[]` as long as `id_entidad_bancaria` is provided.
    """

    base_url = getattr(settings, 'SUDEBAN_API_URL', None)
    if not base_url:
        return {
            'success': False,
            'error': 'missing_config',
            'detail': 'SUDEBAN_API_URL is not configured',
        }

    client = SudebanAPIClient(
        base_url=base_url,
        username=settings.SUDEBAN_USERNAME,
        password=settings.SUDEBAN_PASSWORD,
        verify_ssl=not settings.DEBUG,
    )

    ente_code = id_entidad_bancaria or (resultados[0].codigo_ente_supervisado if resultados else None)
    if not ente_code:
        return {
            'success': False,
            'error': 'missing_ente_code',
            'detail': 'idEntidadBancaria is required when sending without transacciones',
        }

    batch = ResultadoSudebanRequestSchema(
        idEntidadBancaria=ente_code,
        transacciones=[prepare_for_sudeban(r) for r in resultados],
        webhookUrl=webhook_url,
    )

    result = client.send_transaction(
        'resultados-subasta',
        batch.dict(),
    )

    if result.get('success'):
        with db_transaction.atomic():
            for r in resultados:
                r.status = TransactionStatus.SENT
                r.last_sent_at = timezone.now()
                r.error_code = None
                r.error_detail = None
                r.response_data = result.get('data')
                r.save(update_fields=['status', 'last_sent_at', 'error_code', 'error_detail', 'response_data', 'updated_at'])

        return {
            'success': True,
            'count': len(resultados),
            'response': result.get('data'),
        }

    detail = result.get('detail')
    extracted_code = extract_sudeban_error_code(detail)
    decoded_messages = decode_sudeban_error(extracted_code, api='API-03') if extracted_code else None
    if isinstance(detail, str):
        detail_text = detail
    else:
        try:
            detail_text = json.dumps(detail, ensure_ascii=False)
        except Exception:
            detail_text = str(detail)

    with db_transaction.atomic():
        for r in resultados:
            r.status = TransactionStatus.FAILED
            r.retry_count += 1
            r.error_code = extracted_code
            r.error_detail = '; '.join(decoded_messages) if decoded_messages else detail_text
            r.response_data = detail
            r.save(update_fields=['status', 'retry_count', 'error_code', 'error_detail', 'response_data', 'updated_at'])

    return {
        'success': False,
        'error': result.get('error'),
        'detail': result.get('detail'),
    }


def send_pending_resultados(webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Send ALL pending resultados subasta to SUDEBAN synchronously."""

    pendientes = list(
        ResultadoSubasta.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    )
    total_pending = len(pendientes)

    if total_pending == 0:
        ente_code = getattr(settings, 'SUDEBAN_ID_ENTIDAD_BANCARIA', None)
        if not ente_code:
            last = ResultadoSubasta.objects.order_by('-created_at').first()
            ente_code = last.codigo_ente_supervisado if last else None

        if not ente_code:
            return {
                'success': False,
                'total_pending': 0,
                'sent': 0,
                'rejected': 0,
                'failed': 0,
                'error': 'missing_ente_code',
                'detail': 'Configure SUDEBAN_ID_ENTIDAD_BANCARIA to send an empty transacciones payload',
                'groups': {},
            }

        result = send_to_sudeban([], webhook_url=webhook_url, id_entidad_bancaria=ente_code)
        return {
            'success': bool(result.get('success')),
            'total_pending': 0,
            'sent': 0,
            'rejected': 0,
            'failed': 0,
            'groups': {
                ente_code: {
                    'success': bool(result.get('success')),
                    'count': 0,
                    'detail': result.get('detail'),
                    'response': result.get('response') or result.get('data'),
                }
            },
        }

    valid_by_ente: Dict[str, List[ResultadoSubasta]] = defaultdict(list)
    rejected_ids: List[int] = []

    for resultado in pendientes:
        is_valid, errors = validate_resultado_for_sudeban(resultado)
        if not is_valid:
            resultado.status = TransactionStatus.REJECTED
            resultado.error_detail = '; '.join(errors)
            resultado.save(update_fields=['status', 'error_detail', 'updated_at'])
            rejected_ids.append(resultado.id)
            continue
        valid_by_ente[resultado.codigo_ente_supervisado].append(resultado)

    sent_count = 0
    failed_count = 0
    groups: Dict[str, Any] = {}

    for ente, items in valid_by_ente.items():
        result = send_to_sudeban(items, webhook_url=webhook_url)
        groups[ente] = {
            'success': bool(result.get('success')),
            'count': len(items),
            'detail': result.get('detail'),
            'response': result.get('response') or result.get('data'),
        }
        if result.get('success'):
            sent_count += len(items)
        else:
            failed_count += len(items)

    return {
        'success': failed_count == 0,
        'total_pending': total_pending,
        'sent': sent_count,
        'rejected': len(rejected_ids),
        'failed': failed_count,
        'groups': groups,
    }
