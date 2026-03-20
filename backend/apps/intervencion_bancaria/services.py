import logging
import json
from decimal import Decimal
from typing import Dict, Any, Optional, List
from datetime import datetime
from collections import defaultdict

from django.db import transaction as db_transaction
from django.conf import settings
from django.utils import timezone

from .models import IntervencionTransaccion
from .serializers import IntervencionTransaccionInput, IntervencionCorreccionInput
from .sudeban_schemas import SudebanRequestSchema, SudebanTransaccionSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import (
    format_date_for_sudeban,
    format_amount,
    decode_sudeban_error,
    extract_sudeban_error_code,
)
from apps.core.models import TransactionStatus

logger = logging.getLogger(__name__)


def create_transaccion(data: IntervencionTransaccionInput) -> IntervencionTransaccion:
    """
    Create a new transaction from internal data
    """
    with db_transaction.atomic():
        # Check for duplicates
        if IntervencionTransaccion.objects.filter(
            codigo_identificacion_intervencion=data.codigo_identificacion_intervencion
        ).exists():
            raise ValueError(f"Transaction with code {data.codigo_identificacion_intervencion} already exists")
        
        # Calculate contravalor if not provided
        contravalor = data.contravalor_bs
        if not contravalor and data.monto_divisa and data.tipo_cambio_bs:
            contravalor = data.monto_divisa * data.tipo_cambio_bs
        
        transaccion = IntervencionTransaccion.objects.create(
            codigo_ente_supervisado=data.codigo_ente_supervisado,
            tipo_intervencion=data.tipo_intervencion,
            fecha_intervencion=data.fecha_intervencion,
            codigo_identificacion_intervencion=data.codigo_identificacion_intervencion,
            fecha_operacion_cliente=data.fecha_operacion_cliente,
            moneda=data.moneda,
            identificacion_cliente=data.identificacion_cliente.upper(),
            nombre_cliente=data.nombre_cliente,
            actividad_economica_cliente=data.actividad_economica_cliente,
            monto_divisa=data.monto_divisa,
            tipo_cambio_bs=data.tipo_cambio_bs,
            contravalor_bs=contravalor,
            codigo_cuenta_moneda_nacional=data.codigo_cuenta_moneda_nacional or '0',
            tipo_cuenta_moneda_nacional=data.tipo_cuenta_moneda_nacional or 0,
            codigo_cuenta_moneda_extranjera=data.codigo_cuenta_moneda_extranjera or '0',
            tipo_cuenta_moneda_extranjera=data.tipo_cuenta_moneda_extranjera or 0,
            destino_fondos=data.destino_fondos,
            medio_pago=data.medio_pago,
        )
        
        logger.info(f"Created transaction: {transaccion.codigo_identificacion_intervencion}")
        return transaccion


def validate_transaction_for_sudeban(transaccion: IntervencionTransaccion) -> tuple[bool, list]:
    """
    Validate transaction against SUDEBAN business rules
    Returns (is_valid, errors)
    """
    errors = []
    
    # Rule 1: RIF validation (already done in serializer)
    # Rule 2: Currency not Bolivar
    if transaccion.moneda == 928:
        errors.append("Moneda no puede ser Bolívar (928)")
    
    # Rule 3: Monto > 0
    if transaccion.monto_divisa <= 0:
        errors.append("Monto divisa debe ser mayor que 0")
    
    # Rule 4: Tipo cambio > 0
    if transaccion.tipo_cambio_bs <= 0:
        errors.append("Tipo cambio debe ser mayor que 0")
    
    # Rule 5: Account validation based on intervention type
    venta_interventions = ['1', '3', '7']
    if transaccion.tipo_intervencion in venta_interventions:
        # Must have valid accounts
        if len(transaccion.codigo_cuenta_moneda_nacional) != 20:
            errors.append("Cuenta nacional debe tener 20 dígitos para ventas")
        if len(transaccion.codigo_cuenta_moneda_extranjera) != 20:
            errors.append("Cuenta extranjera debe tener 20 dígitos para ventas")
        if transaccion.tipo_cuenta_moneda_nacional not in [8, 9, 10]:
            errors.append("Tipo cuenta nacional debe ser 8, 9 o 10 para ventas")
        if transaccion.tipo_cuenta_moneda_extranjera not in [31, 32]:
            errors.append("Tipo cuenta extranjera debe ser 31 o 32 para ventas")
    else:
        # Not a sale, accounts should be '0 - No Aplica'
        if transaccion.codigo_cuenta_moneda_nacional != '0':
            errors.append("Para este tipo de intervención, cuenta nacional debe ser 0")
        if transaccion.codigo_cuenta_moneda_extranjera != '0':
            errors.append("Para este tipo de intervención, cuenta extranjera debe ser 0")
    
    # Rule 6: Destino fondos validation
    if transaccion.tipo_intervencion in venta_interventions:
        if transaccion.destino_fondos == 0:
            errors.append("Destino fondos no puede ser 0 para ventas")
    else:
        if transaccion.destino_fondos != 0:
            errors.append("Para este tipo de intervención, destino fondos debe ser 0")
    
    # Rule 7: Medio pago validation
    if transaccion.medio_pago == 0:
        errors.append("Medio pago no puede ser 0")
    
    return len(errors) == 0, errors


def prepare_for_sudeban(transaccion: IntervencionTransaccion) -> SudebanTransaccionSchema:
    """
    Prepare a transaction for SUDEBAN format
    """
    return SudebanTransaccionSchema(
        idTipIntervencion=transaccion.tipo_intervencion,
        fechalIntervencion=format_date_for_sudeban(transaccion.fecha_intervencion),
        codigolIntervencion=transaccion.codigo_identificacion_intervencion,
        fechaOperacionCliente=format_date_for_sudeban(transaccion.fecha_operacion_cliente),
        idMoneda=transaccion.moneda,
        rifCiCliente=transaccion.identificacion_cliente,
        nombreCliente=transaccion.nombre_cliente,
        idActEconomicaCliente=transaccion.actividad_economica_cliente,
        montoDivisa=format_amount(transaccion.monto_divisa, 4),
        tasaCambioBs=format_amount(transaccion.tipo_cambio_bs, 4),
        contravalorBs=format_amount(transaccion.contravalor_bs, 4),
        nroCtaBancariaCliente=transaccion.codigo_cuenta_moneda_nacional,
        idTipoCtaBancariaCliente=transaccion.tipo_cuenta_moneda_nacional,
        nroCtaBancariaExtCliente=transaccion.codigo_cuenta_moneda_extranjera,
        idTipoCtaBancariaExtCliente=transaccion.tipo_cuenta_moneda_extranjera,
        idDestinoFondos=transaccion.destino_fondos,
        idMedioPago=transaccion.medio_pago,
    )


def send_to_sudeban(
    transacciones: List[IntervencionTransaccion],
    webhook_url: str = None,
    id_entidad_bancaria: Optional[str] = None,
) -> Dict[str, Any]:
    """Send batch of transactions to SUDEBAN (API-01).

    If `transacciones` is empty, the function will still transmit a payload with
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
    
    # Prepare batch
    ente_code = id_entidad_bancaria or (transacciones[0].codigo_ente_supervisado if transacciones else None)
    if not ente_code:
        return {
            'success': False,
            'error': 'missing_ente_code',
            'detail': 'idEntidadBancaria is required when sending without transacciones',
        }
    batch = SudebanRequestSchema(
        idEntidadBancaria=ente_code,
        transacciones=[prepare_for_sudeban(t) for t in transacciones],
        webhookUrl=webhook_url
    )
    
    # Send
    result = client.send_transaction(
        'intervencion-cambiaria',
        batch.dict()
    )
    
    if result['success']:
        # Update sent transactions
        with db_transaction.atomic():
            for t in transacciones:
                t.status = 'sent'
                t.last_sent_at = timezone.now()
                t.error_code = None
                t.error_detail = None
                t.response_data = result.get('data')
                t.save()
        
        return {
            'success': True,
            'count': len(transacciones),
            'response': result.get('data')
        }
    else:
        # Handle error - mark as failed but track error
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
            for t in transacciones:
                t.status = 'failed'
                t.retry_count += 1
                t.error_code = extracted_code
                t.error_detail = '; '.join(decoded_messages) if decoded_messages else detail_text
                t.response_data = detail
                t.save()
        
        return {
            'success': False,
            'error': result.get('error'),
            'detail': result.get('detail')
        }


def correct_transaccion(transaccion_id: int, data: IntervencionCorreccionInput) -> IntervencionTransaccion:
    """
    Apply corrections to a rejected transaction
    """
    with db_transaction.atomic():
        transaccion = IntervencionTransaccion.objects.get(id=transaccion_id)
        
        if transaccion.status != 'rejected':
            raise ValueError("Only rejected transactions can be corrected")
        
        # Apply corrections
        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if value is not None and hasattr(transaccion, field):
                setattr(transaccion, field, value)
                update_fields.append(field)
        
        # Reset status to pending for resending
        transaccion.status = 'pending'
        transaccion.error_code = None
        transaccion.error_detail = None
        transaccion.retry_count = 0
        update_fields.extend(['status', 'error_code', 'error_detail', 'retry_count'])
        
        transaccion.save(update_fields=update_fields)
        
        logger.info(f"Corrected transaction {transaccion_id}")
        return transaccion


def send_pending_transacciones(webhook_url: Optional[str] = None) -> Dict[str, Any]:
    """Send ALL pending intervencion transacciones to SUDEBAN synchronously."""

    pendientes = list(
        IntervencionTransaccion.objects.filter(status=TransactionStatus.PENDING).order_by('created_at')
    )
    total_pending = len(pendientes)

    if total_pending == 0:
        ente_code = getattr(settings, 'SUDEBAN_ID_ENTIDAD_BANCARIA', None)
        if not ente_code:
            last = IntervencionTransaccion.objects.order_by('-created_at').first()
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

    valid_by_ente: Dict[str, List[IntervencionTransaccion]] = defaultdict(list)
    rejected_ids: List[int] = []

    for transaccion in pendientes:
        is_valid, errors = validate_transaction_for_sudeban(transaccion)
        if not is_valid:
            transaccion.status = TransactionStatus.REJECTED
            transaccion.error_detail = '; '.join(errors)
            transaccion.save(update_fields=['status', 'error_detail', 'updated_at'])
            rejected_ids.append(transaccion.id)
            continue
        valid_by_ente[transaccion.codigo_ente_supervisado].append(transaccion)

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