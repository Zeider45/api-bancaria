import logging
import json
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict

from django.db import transaction as db_transaction
from django.conf import settings
from django.utils import timezone

from .models import OperacionMesaDeCambio
from .serializers import OperacionMesaDeCambioInput, OperacionMesaDeCambioCorreccionInput
from .sudeban_schemas import SudebanMesaDeCambioRequestSchema, SudebanMesaDeCambioTransaccionSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import (
    format_date_for_sudeban,
    format_amount,
    decode_sudeban_error,
    extract_sudeban_error_code,
)
from apps.core.models import TransactionStatus
from apps.core import selectors as core_selectors

logger = logging.getLogger(__name__)


def create_operacion(data: OperacionMesaDeCambioInput) -> OperacionMesaDeCambio:
    """
    Create a new mesa de cambio transaction from internal data.
    """
    with db_transaction.atomic():
        # Calculate contravalor if not provided
        contravalor = data.contravalor_bs
        if not contravalor and data.monto_divisa and data.tipo_cambio_bs:
            contravalor = data.monto_divisa * data.tipo_cambio_bs

        operacion = OperacionMesaDeCambio.objects.create(
            identificacion_ente_supervisado=data.identificacion_ente_supervisado,
            tipo_pacto=data.tipo_pacto,
            moneda=data.moneda,
            fecha_pacto=data.fecha_pacto,
            monto_divisa=data.monto_divisa,
            tipo_cambio_bs=data.tipo_cambio_bs,
            contravalor_bs=contravalor,
            identificacion_cliente_oferente=data.identificacion_cliente_oferente.upper(),
            nombre_cliente_oferente=data.nombre_cliente_oferente,
            actividad_economica_cliente_oferente=data.actividad_economica_cliente_oferente,
            codigo_cuenta_moneda_nacional_oferente=data.codigo_cuenta_moneda_nacional_oferente,
            tipo_cuenta_moneda_nacional_cliente_oferente=data.tipo_cuenta_moneda_nacional_cliente_oferente,
            codigo_cuenta_moneda_extranjera_oferente=data.codigo_cuenta_moneda_extranjera_oferente,
            tipo_cuenta_moneda_extranjera_cliente_oferente=data.tipo_cuenta_moneda_extranjera_cliente_oferente,
            origen_fondos=data.origen_fondos,
            medio_pago_oferente=data.medio_pago_oferente,
            identificacion_cliente_demandante=data.identificacion_cliente_demandante.upper(),
            nombre_cliente_demandante=data.nombre_cliente_demandante,
            actividad_economica_cliente_demandante=data.actividad_economica_cliente_demandante,
            codigo_cuenta_moneda_nacional_demandante=data.codigo_cuenta_moneda_nacional_demandante,
            tipo_cuenta_moneda_nacional_cliente_demandante=data.tipo_cuenta_moneda_nacional_cliente_demandante,
            codigo_cuenta_moneda_extranjera_demandante=data.codigo_cuenta_moneda_extranjera_demandante,
            tipo_cuenta_moneda_extranjera_cliente_demandante=data.tipo_cuenta_moneda_extranjera_cliente_demandante,
            destino_fondos=data.destino_fondos,
            medio_pago_demandante=data.medio_pago_demandante,
        )

        logger.info(f"Created mesa de cambio transaction id={operacion.id}")
        return operacion


def validate_operacion_for_sudeban(operacion: OperacionMesaDeCambio) -> Tuple[bool, List[str]]:
    """
    Validate a mesa de cambio transaction against SUDEBAN business rules.
    Returns (is_valid, errors).
    """
    errors = []

    # Rule 1: Monto divisa > 0
    if operacion.monto_divisa <= 0:
        errors.append("Monto Divisa debe ser mayor que 0")

    # Rule 2: Tipo cambio > 0
    if operacion.tipo_cambio_bs <= 0:
        errors.append("Tipo de Cambio Bs debe ser mayor que 0")

    # Rule 3: Contravalor > 0
    if operacion.contravalor_bs <= 0:
        errors.append("Contravalor en Bs debe ser mayor que 0")

    # Rule 4: Cuenta nacional oferente must be 20 digits
    if not operacion.codigo_cuenta_moneda_nacional_oferente.isdigit() or \
            len(operacion.codigo_cuenta_moneda_nacional_oferente) != 20:
        errors.append("Código Cuenta Moneda Nacional Oferente debe ser un número de 20 dígitos")

    # Rule 5: Tipo cuenta nacional oferente must be 8, 9 or 10
    if operacion.tipo_cuenta_moneda_nacional_cliente_oferente not in (8, 9, 10):
        errors.append("Tipo Cuenta Moneda Nacional Cliente Oferente debe ser 8, 9 o 10")

    # Rule 6: Cuenta extranjera oferente must be 20 digits
    if not operacion.codigo_cuenta_moneda_extranjera_oferente.isdigit() or \
            len(operacion.codigo_cuenta_moneda_extranjera_oferente) != 20:
        errors.append("Código Cuenta Moneda Extranjera Oferente debe ser un número de 20 dígitos")

    # Rule 7: Tipo cuenta extranjera oferente must be 31 or 32
    if operacion.tipo_cuenta_moneda_extranjera_cliente_oferente not in (31, 32):
        errors.append("Tipo Cuenta Moneda Extranjera Cliente Oferente debe ser 31 o 32")

    # Rule 8: Cuenta nacional demandante must be 20 digits
    if not operacion.codigo_cuenta_moneda_nacional_demandante.isdigit() or \
            len(operacion.codigo_cuenta_moneda_nacional_demandante) != 20:
        errors.append("Código Cuenta Moneda Nacional Demandante debe ser un número de 20 dígitos")

    # Rule 9: Tipo cuenta nacional demandante (Destino) must be a positive code
    if operacion.tipo_cuenta_moneda_nacional_cliente_demandante is None or operacion.tipo_cuenta_moneda_nacional_cliente_demandante <= 0:
        errors.append("Tipo Cuenta Moneda Nacional Cliente Demandante debe ser un entero mayor que 0")

    # Rule 10: Cuenta extranjera demandante must be 20 digits
    if not operacion.codigo_cuenta_moneda_extranjera_demandante.isdigit() or \
            len(operacion.codigo_cuenta_moneda_extranjera_demandante) != 20:
        errors.append("Código Cuenta Moneda Extranjera Demandante debe ser un número de 20 dígitos")

    # Rule 11: Tipo cuenta extranjera demandante (Destino) must be a positive code
    if operacion.tipo_cuenta_moneda_extranjera_cliente_demandante is None or operacion.tipo_cuenta_moneda_extranjera_cliente_demandante <= 0:
        errors.append("Tipo Cuenta Moneda Extranjera Cliente Demandante debe ser un entero mayor que 0")

    # Rule 12: Nombres no vacíos
    if not operacion.nombre_cliente_oferente.strip():
        errors.append("Nombre Cliente Oferente no puede estar vacío")

    if not operacion.nombre_cliente_demandante.strip():
        errors.append("Nombre Cliente Demandante no puede estar vacío")

    # Rule 13: Ente Supervisado must exist in catalog
    if not core_selectors.is_valid_ente_supervisado(operacion.identificacion_ente_supervisado):
        errors.append("Identificación Ente Supervisado inválida (no existe en el catálogo)")

    # Rule 14: Moneda must exist in catalog (uses numeric ISO code in catalog)
    if not core_selectors.is_valid_moneda(operacion.moneda):
        errors.append("Moneda inválida (no existe en el catálogo)")

    # Rule 15: Actividad económica must exist in catalog
    if not core_selectors.is_valid_actividad_economica(operacion.actividad_economica_cliente_oferente):
        errors.append("Actividad Económica Cliente Oferente inválida (no existe en el catálogo)")
    if not core_selectors.is_valid_actividad_economica(operacion.actividad_economica_cliente_demandante):
        errors.append("Actividad Económica Cliente Demandante inválida (no existe en el catálogo)")

    # Rule 16: Origen/Destino fondos and medios de pago must exist in catalogs
    if not core_selectors.is_valid_destino_fondos(operacion.origen_fondos):
        errors.append("Origen Fondos inválido (no existe en el catálogo)")
    if not core_selectors.is_valid_destino_fondos(operacion.destino_fondos):
        errors.append("Destino Fondos inválido (no existe en el catálogo)")
    if not core_selectors.is_valid_medio_pago(operacion.medio_pago_oferente):
        errors.append("Medio Pago Oferente inválido (no existe en el catálogo)")
    if not core_selectors.is_valid_medio_pago(operacion.medio_pago_demandante):
        errors.append("Medio Pago Demandante inválido (no existe en el catálogo)")

    return len(errors) == 0, errors


def prepare_for_sudeban(operacion: OperacionMesaDeCambio) -> SudebanMesaDeCambioTransaccionSchema:
    """
    Prepare a mesa de cambio transaction in the exact SUDEBAN format.
    """
    return SudebanMesaDeCambioTransaccionSchema(
        idTipoPacto=operacion.tipo_pacto,
        idMoneda=int(str(operacion.moneda).strip()),
        fechaPacto=format_date_for_sudeban(operacion.fecha_pacto),
        montoDivisa=format_amount(operacion.monto_divisa, 4),
        tasaCambioBs=format_amount(operacion.tipo_cambio_bs, 4),
        contravalorBs=format_amount(operacion.contravalor_bs, 4),

        rifCiOrigen=operacion.identificacion_cliente_oferente,
        nombreClienteOrigen=operacion.nombre_cliente_oferente,
        idActEconomicaOrigen=operacion.actividad_economica_cliente_oferente,
        nroCtaBancariaOrigen=operacion.codigo_cuenta_moneda_nacional_oferente,
        idTipoCtaBancariaOrigen=operacion.tipo_cuenta_moneda_nacional_cliente_oferente,
        nroCtaBancariaExtOrigen=operacion.codigo_cuenta_moneda_extranjera_oferente,
        idTipoCtaBancariaExtOrigen=operacion.tipo_cuenta_moneda_extranjera_cliente_oferente,
        idOrigenFondos=int(str(operacion.origen_fondos).strip()),
        idMedioPagoOrigen=int(str(operacion.medio_pago_oferente).strip()),

        rifCiDestino=operacion.identificacion_cliente_demandante,
        nombreClienteDestino=operacion.nombre_cliente_demandante,
        idActEconomicaDestino=operacion.actividad_economica_cliente_demandante,
        nroCtaBancariaDestino=operacion.codigo_cuenta_moneda_nacional_demandante,
        idTipoCtaBancariaDestino=operacion.tipo_cuenta_moneda_nacional_cliente_demandante,
        nroCtaBancariaExtDestino=operacion.codigo_cuenta_moneda_extranjera_demandante,
        idTipoCtaBancariaExtDestino=operacion.tipo_cuenta_moneda_extranjera_cliente_demandante,
        idDestinoFondos=int(str(operacion.destino_fondos).strip()),
        idMedioPagoDestino=int(str(operacion.medio_pago_demandante).strip()),
    )


def send_to_sudeban(
    operaciones: List[OperacionMesaDeCambio],
    webhook_url: str = None,
    id_entidad_bancaria: str = None,
) -> Dict[str, Any]:
    """
    Send a batch of mesa de cambio transactions to SUDEBAN.
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

    ente_code = id_entidad_bancaria or (operaciones[0].identificacion_ente_supervisado if operaciones else None)
    if not ente_code:
        return {
            'success': False,
            'error': 'missing_ente_code',
            'detail': 'idEntidadBancaria is required when sending without transacciones',
        }
    batch = SudebanMesaDeCambioRequestSchema(
        idEntidadBancaria=ente_code,
        transacciones=[prepare_for_sudeban(op) for op in operaciones],
        webhookUrl=webhook_url,
    )

    result = client.send_transaction(
        'mesa-de-cambio',
        batch.dict(),
    )

    if result['success']:
        with db_transaction.atomic():
            for op in operaciones:
                op.status = 'sent'
                op.last_sent_at = timezone.now()
                op.error_code = None
                op.error_detail = None
                op.response_data = result.get('data')
                op.save()

        return {
            'success': True,
            'count': len(operaciones),
            'response': result.get('data'),
        }
    else:
        detail = result.get('detail')
        extracted_code = extract_sudeban_error_code(detail)
        decoded_messages = decode_sudeban_error(extracted_code) if extracted_code else None
        if isinstance(detail, str):
            detail_text = detail
        else:
            try:
                detail_text = json.dumps(detail, ensure_ascii=False)
            except Exception:
                detail_text = str(detail)

        with db_transaction.atomic():
            for op in operaciones:
                op.status = 'failed'
                op.retry_count += 1
                op.error_code = extracted_code
                op.error_detail = '; '.join(decoded_messages) if decoded_messages else detail_text
                op.response_data = detail
                op.save()

        return {
            'success': False,
            'error': result.get('error'),
            'detail': result.get('detail'),
        }


def correct_operacion(
    operacion_id: int,
    data: OperacionMesaDeCambioCorreccionInput,
) -> OperacionMesaDeCambio:
    """
    Apply corrections to a rejected mesa de cambio transaction and reset it to pending.
    """
    with db_transaction.atomic():
        operacion = OperacionMesaDeCambio.objects.get(id=operacion_id)

        if operacion.status != 'rejected':
            raise ValueError("Only rejected transactions can be corrected")

        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if value is not None and hasattr(operacion, field):
                setattr(operacion, field, value)
                update_fields.append(field)

        # Reset status to pending for resending
        operacion.status = 'pending'
        operacion.error_code = None
        operacion.error_detail = None
        operacion.retry_count = 0
        update_fields.extend(['status', 'error_code', 'error_detail', 'retry_count'])

        operacion.save(update_fields=update_fields)

        logger.info(f"Corrected mesa de cambio transaction id={operacion_id}")
        return operacion


def send_pending_operaciones(webhook_url: str = None) -> Dict[str, Any]:
    """Send ALL pending mesa de cambio operaciones to SUDEBAN synchronously."""

    pendientes = list(
        OperacionMesaDeCambio.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    )
    total_pending = len(pendientes)

    if total_pending == 0:
        ente_code = getattr(settings, 'SUDEBAN_ID_ENTIDAD_BANCARIA', None)
        if not ente_code:
            last = OperacionMesaDeCambio.objects.order_by('-created_at').first()
            ente_code = last.identificacion_ente_supervisado if last else None

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

    valid_by_ente: Dict[str, List[OperacionMesaDeCambio]] = defaultdict(list)
    rejected_ids: List[int] = []

    for operacion in pendientes:
        is_valid, errors = validate_operacion_for_sudeban(operacion)
        if not is_valid:
            operacion.status = TransactionStatus.REJECTED
            operacion.error_detail = '; '.join(errors)
            operacion.save(update_fields=['status', 'error_detail', 'updated_at'])
            rejected_ids.append(operacion.id)
            continue

        valid_by_ente[operacion.identificacion_ente_supervisado].append(operacion)

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
