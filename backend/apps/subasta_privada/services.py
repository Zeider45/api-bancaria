import logging
import json
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from django.db import transaction as db_transaction
from django.conf import settings
from django.utils import timezone

from .models import SubastaSolicitud
from .serializers import SubastaSolicitudInput, SubastaCorreccionInput
from .sudeban_schemas import SudebanRequestSchema, SudebanSolicitudSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import (
    format_date_for_sudeban,
    format_amount,
    decode_sudeban_error,
    extract_sudeban_error_code,
    get_sudeban_ente_supervisado,
)
from apps.core.models import TransactionStatus

logger = logging.getLogger(__name__)


def create_solicitud(data: SubastaSolicitudInput) -> SubastaSolicitud:
    """
    Create a new subasta request from internal data
    """
    with db_transaction.atomic():
        # Check for duplicates
        if SubastaSolicitud.objects.filter(
            codigo_identificacion_subasta=data.codigo_identificacion_subasta
        ).exists():
            raise ValueError(f"Solicitud with code {data.codigo_identificacion_subasta} already exists")
        
        # Calculate contravalor if not provided
        contravalor = data.contravalor_bs
        if not contravalor and data.monto_divisa and data.tipo_cambio_bs:
            contravalor = data.monto_divisa * data.tipo_cambio_bs
        
        solicitud = SubastaSolicitud.objects.create(
            codigo_ente_supervisado=get_sudeban_ente_supervisado(),
            fecha_subasta=data.fecha_subasta,
            codigo_identificacion_subasta=data.codigo_identificacion_subasta,
            fecha_solicitud_cliente=data.fecha_solicitud_cliente,
            moneda=data.moneda,
            identificacion_cliente=data.identificacion_cliente.upper(),
            nombre_cliente=data.nombre_cliente,
            actividad_economica_cliente=data.actividad_economica_cliente,
            monto_divisa=data.monto_divisa,
            tipo_cambio_bs=data.tipo_cambio_bs,
            contravalor_bs=contravalor,
            codigo_cuenta_moneda_nacional=data.codigo_cuenta_moneda_nacional,
            tipo_cuenta_moneda_nacional=data.tipo_cuenta_moneda_nacional,
            codigo_cuenta_moneda_extranjera=data.codigo_cuenta_moneda_extranjera,
            tipo_cuenta_moneda_extranjera=data.tipo_cuenta_moneda_extranjera,
            destino_fondos=data.destino_fondos,
            medio_pago=data.medio_pago,
        )
        
        logger.info(f"Created subasta request: {solicitud.codigo_identificacion_subasta}")
        return solicitud


def validate_solicitud_for_sudeban(solicitud: SubastaSolicitud) -> tuple[bool, list]:
    """
    Validate subasta request against SUDEBAN business rules (API-02)
    """
    errors = []
    
    # Rule 1: RIF validation (already done in serializer)
    
    # Rule 2: Currency not Bolivar
    if solicitud.moneda == 928:
        errors.append("Moneda no puede ser Bolívar (928)")
    
    # Rule 3: Monto > 0
    if solicitud.monto_divisa <= 0:
        errors.append("Monto divisa debe ser mayor que 0")
    
    # Rule 4: Tipo cambio > 0
    if solicitud.tipo_cambio_bs <= 0:
        errors.append("Tipo cambio debe ser mayor que 0")
    
    # Rule 5: fecha_solicitud_cliente must equal fecha_subasta
    if solicitud.fecha_solicitud_cliente.date() != solicitud.fecha_subasta.date():
        errors.append("fecha_solicitud_cliente debe ser igual a fecha_subasta")
    
    # Rule 6: Account validations (always required for subasta)
    if len(solicitud.codigo_cuenta_moneda_nacional) != 20:
        errors.append("Cuenta nacional debe tener 20 dígitos")
    
    if solicitud.tipo_cuenta_moneda_nacional not in [8, 9, 10]:
        errors.append("Tipo cuenta nacional debe ser 8, 9 o 10")
    
    if len(solicitud.codigo_cuenta_moneda_extranjera) != 20:
        errors.append("Cuenta extranjera debe tener 20 dígitos")
    
    if solicitud.tipo_cuenta_moneda_extranjera not in [31, 32]:
        errors.append("Tipo cuenta extranjera debe ser 31 o 32")
    
    # Rule 7: Destino fondos cannot be 0
    if solicitud.destino_fondos == 0:
        errors.append("Destino fondos no puede ser 0")
    
    # Rule 8: Medio pago must be 2
    if solicitud.medio_pago != 2:
        errors.append("Medio pago debe ser 2 (Transferencia a Cuenta Cliente)")
    
    return len(errors) == 0, errors


def prepare_for_sudeban(solicitud: SubastaSolicitud) -> SudebanSolicitudSchema:
    """
    Prepare a subasta request for SUDEBAN format (API-02)
    """
    return SudebanSolicitudSchema(
        fechaSubasta=format_date_for_sudeban(solicitud.fecha_subasta),
        codigoSubasta=solicitud.codigo_identificacion_subasta,
        fechaSolicitudCliente=format_date_for_sudeban(solicitud.fecha_solicitud_cliente),
        idMoneda=solicitud.moneda,
        rifCiCliente=solicitud.identificacion_cliente,
        nombreCliente=solicitud.nombre_cliente,
        idActEconomicaCliente=solicitud.actividad_economica_cliente,
        montoDivisa=format_amount(solicitud.monto_divisa, 4),
        tasaCambioBs=format_amount(solicitud.tipo_cambio_bs, 4),
        contravalorBs=format_amount(solicitud.contravalor_bs, 4),
        nroCtaBancariaCliente=solicitud.codigo_cuenta_moneda_nacional,
        idTipoCtaBancariaCliente=solicitud.tipo_cuenta_moneda_nacional,
        nroCtaBancariaExtCliente=solicitud.codigo_cuenta_moneda_extranjera,
        idTipoCtaBancariaExtCliente=solicitud.tipo_cuenta_moneda_extranjera,
        idDestinoFondos=solicitud.destino_fondos,
        idMedioPago=solicitud.medio_pago,
    )


def send_to_sudeban(
    solicitudes: List[SubastaSolicitud],
    webhook_url: str = None,
    id_entidad_bancaria: Optional[str] = None,
) -> Dict[str, Any]:
    """Send a batch of subasta requests to SUDEBAN (API-02).

    If `solicitudes` is empty, the function will still transmit a payload with
    `transacciones=[]` ("sin transacciones") as long as `id_entidad_bancaria`
    is provided.
    """

    base_url = getattr(settings, 'SUDEBAN_API_URL', None)
    if not base_url:
        return {
            'success': False,
            'error': 'missing_config',
            'detail': 'SUDEBAN_API_URL is not configured',
        }
    
    # Get client configuration
    client = SudebanAPIClient(
        base_url=base_url,
        username=settings.SUDEBAN_USERNAME,
        password=settings.SUDEBAN_PASSWORD,
        verify_ssl=not settings.DEBUG  # Only skip SSL in dev
    )
    
    # Prepare batch (all from same entity)
    ente_code = id_entidad_bancaria or (solicitudes[0].codigo_ente_supervisado if solicitudes else None)
    if not ente_code:
        return {
            'success': False,
            'error': 'missing_ente_code',
            'detail': 'idEntidadBancaria is required when sending without transacciones',
        }
    batch = SudebanRequestSchema(
        idEntidadBancaria=ente_code,
        transacciones=[prepare_for_sudeban(s) for s in solicitudes],
        webhookUrl=webhook_url
    )
    
    # Send to SUDEBAN (API-02 endpoint)
    result = client.send_transaction(
        'libro-ordenes-subasta',  # Endpoint for API-02
        batch.dict()
    )
    
    if result['success']:
        # Update sent requests
        with db_transaction.atomic():
            for s in solicitudes:
                s.status = 'sent'
                s.last_sent_at = timezone.now()
                s.error_code = None
                s.error_detail = None
                s.response_data = result.get('data')
                s.save()
        
        return {
            'success': True,
            'count': len(solicitudes),
            'response': result.get('data'),
        }
    else:
        # Handle error - mark as failed but track error
        detail = result.get('detail')
        extracted_code = extract_sudeban_error_code(detail)
        decoded_messages = decode_sudeban_error(extracted_code, api='API-02') if extracted_code else None
        if isinstance(detail, str):
            detail_text = detail
        else:
            try:
                detail_text = json.dumps(detail, ensure_ascii=False)
            except Exception:
                detail_text = str(detail)

        with db_transaction.atomic():
            for s in solicitudes:
                s.status = 'failed'
                s.retry_count += 1
                s.error_code = extracted_code
                s.error_detail = '; '.join(decoded_messages) if decoded_messages else detail_text
                s.response_data = detail
                s.save()
        
        return {
            'success': False,
            'error': result.get('error'),
            'detail': result.get('detail')
        }


def correct_solicitud(solicitud_id: int, data: SubastaCorreccionInput) -> SubastaSolicitud:
    """
    Apply corrections to a rejected subasta request
    """
    with db_transaction.atomic():
        try:
            solicitud = SubastaSolicitud.objects.get(id=solicitud_id)
        except SubastaSolicitud.DoesNotExist:
            raise ValueError(f"Solicitud {solicitud_id} not found")
        
        if solicitud.status != 'rejected':
            raise ValueError("Only rejected requests can be corrected")
        
        # Apply corrections
        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if value is not None and hasattr(solicitud, field):
                setattr(solicitud, field, value)
                update_fields.append(field)
        
        # Recalculate contravalor if amounts changed
        if 'monto_divisa' in update_fields or 'tipo_cambio_bs' in update_fields:
            solicitud.contravalor_bs = solicitud.monto_divisa * solicitud.tipo_cambio_bs
            update_fields.append('contravalor_bs')
        
        # Reset status to pending for resending
        solicitud.status = 'pending'
        solicitud.error_code = None
        solicitud.error_detail = None
        solicitud.retry_count = 0
        update_fields.extend(['status', 'error_code', 'error_detail', 'retry_count'])
        
        solicitud.save(update_fields=update_fields)
        
        logger.info(f"Corrected subasta request {solicitud_id}")
        return solicitud


def process_sudeban_callback(codigo_subasta: str, status: str, error_code: Optional[int] = None):
    """
    Process callback/webhook from SUDEBAN
    """
    with db_transaction.atomic():
        solicitudes = SubastaSolicitud.objects.filter(
            codigo_identificacion_subasta=codigo_subasta
        )
        
        if status == 'success':
            solicitudes.update(
                status='success',
                error_code=None,
                error_detail=None
            )
            logger.info(f"Subasta {codigo_subasta} confirmed successful")
        elif status == 'rejected' and error_code:
            error_messages = decode_sudeban_error(error_code, api='API-02')
            solicitudes.update(
                status='rejected',
                error_code=error_code,
                error_detail='; '.join(error_messages)
            )
            logger.warning(f"Subasta {codigo_subasta} rejected: {error_messages}")


def send_pending_solicitudes(webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Send ALL pending subasta solicitudes to SUDEBAN synchronously.

    - Only sends `status='pending'`.
    - Validates each item; invalid ones are marked `rejected`.
    - Groups by ente supervisado to respect SUDEBAN request shape.
    """

    pendientes = list(
        SubastaSolicitud.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    )

    total_pending = len(pendientes)
    if total_pending == 0:
        ente_code = getattr(settings, 'SUDEBAN_ID_ENTIDAD_BANCARIA', None)
        if not ente_code:
            last = SubastaSolicitud.objects.order_by('-created_at').first()
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

    valid_by_ente: Dict[str, List[SubastaSolicitud]] = defaultdict(list)
    rejected_ids: List[int] = []

    for solicitud in pendientes:
        is_valid, errors = validate_solicitud_for_sudeban(solicitud)
        if not is_valid:
            solicitud.status = TransactionStatus.REJECTED
            solicitud.error_detail = '; '.join(errors)
            solicitud.save(update_fields=['status', 'error_detail', 'updated_at'])
            rejected_ids.append(solicitud.id)
            continue
        valid_by_ente[solicitud.codigo_ente_supervisado].append(solicitud)

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