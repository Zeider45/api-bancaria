import logging
from decimal import Decimal
from typing import Dict, Any, List, Tuple
from datetime import datetime

from django.db import transaction as db_transaction
from django.conf import settings
from django.utils import timezone

from .models import OperacionMesaDeCambio
from .serializers import OperacionMesaDeCambioInput, OperacionMesaDeCambioCorreccionInput
from .sudeban_schemas import SudebanMesaDeCambioRequestSchema, SudebanMesaDeCambioTransaccionSchema
from apps.core.vpn_client import SudebanAPIClient
from apps.core.utils import format_date_for_sudeban, format_amount

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

    # Rule 9: Tipo cuenta nacional demandante must be 8, 9 or 10
    if operacion.tipo_cuenta_moneda_nacional_cliente_demandante not in (8, 9, 10):
        errors.append("Tipo Cuenta Moneda Nacional Cliente Demandante debe ser 8, 9 o 10")

    # Rule 10: Cuenta extranjera demandante must be 20 digits
    if not operacion.codigo_cuenta_moneda_extranjera_demandante.isdigit() or \
            len(operacion.codigo_cuenta_moneda_extranjera_demandante) != 20:
        errors.append("Código Cuenta Moneda Extranjera Demandante debe ser un número de 20 dígitos")

    # Rule 11: Tipo cuenta extranjera demandante must be 31 or 32
    if operacion.tipo_cuenta_moneda_extranjera_cliente_demandante not in (31, 32):
        errors.append("Tipo Cuenta Moneda Extranjera Cliente Demandante debe ser 31 o 32")

    # Rule 12: Nombres no vacíos
    if not operacion.nombre_cliente_oferente.strip():
        errors.append("Nombre Cliente Oferente no puede estar vacío")

    if not operacion.nombre_cliente_demandante.strip():
        errors.append("Nombre Cliente Demandante no puede estar vacío")

    return len(errors) == 0, errors


def prepare_for_sudeban(operacion: OperacionMesaDeCambio) -> SudebanMesaDeCambioTransaccionSchema:
    """
    Prepare a mesa de cambio transaction in the exact SUDEBAN format.
    """
    return SudebanMesaDeCambioTransaccionSchema(
        tipoPacto=operacion.tipo_pacto,
        moneda=operacion.moneda,
        fechaPacto=format_date_for_sudeban(operacion.fecha_pacto),
        montoDivisa=format_amount(operacion.monto_divisa, 4),
        tipoCambioBs=format_amount(operacion.tipo_cambio_bs, 4),
        contraValorBs=format_amount(operacion.contravalor_bs, 4),
        identificacionClienteOferente=operacion.identificacion_cliente_oferente,
        nombreClienteOferente=operacion.nombre_cliente_oferente,
        actEconomicaClienteOferente=operacion.actividad_economica_cliente_oferente,
        codCtaMnOferente=operacion.codigo_cuenta_moneda_nacional_oferente,
        tipCtaMnClienteOferente=operacion.tipo_cuenta_moneda_nacional_cliente_oferente,
        codCtaMeOferente=operacion.codigo_cuenta_moneda_extranjera_oferente,
        tipCtaMeClienteOferente=operacion.tipo_cuenta_moneda_extranjera_cliente_oferente,
        origenFondos=operacion.origen_fondos,
        medioPagoOferente=operacion.medio_pago_oferente,
        identificacionClienteDemandante=operacion.identificacion_cliente_demandante,
        nombreClienteDemandante=operacion.nombre_cliente_demandante,
        actEconomicaClienteDemandante=operacion.actividad_economica_cliente_demandante,
        codCtaMnDemandante=operacion.codigo_cuenta_moneda_nacional_demandante,
        tipCtaMnClienteDemandante=operacion.tipo_cuenta_moneda_nacional_cliente_demandante,
        codCtaMeDemandante=operacion.codigo_cuenta_moneda_extranjera_demandante,
        tipCtaMeClienteDemandante=operacion.tipo_cuenta_moneda_extranjera_cliente_demandante,
        destinoFondos=operacion.destino_fondos,
        medioPagoDemandante=operacion.medio_pago_demandante,
    )


def send_to_sudeban(
    operaciones: List[OperacionMesaDeCambio],
    webhook_url: str = None,
) -> Dict[str, Any]:
    """
    Send a batch of mesa de cambio transactions to SUDEBAN.
    """
    if not operaciones:
        return {'success': True, 'message': 'No transactions to send'}

    client = SudebanAPIClient(
        base_url=settings.SUDEBAN_API_URL,
        username=settings.SUDEBAN_USERNAME,
        password=settings.SUDEBAN_PASSWORD,
        verify_ssl=not settings.DEBUG,
    )

    ente_code = operaciones[0].identificacion_ente_supervisado
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
                op.save()

        return {
            'success': True,
            'count': len(operaciones),
            'response': result.get('data'),
        }
    else:
        with db_transaction.atomic():
            for op in operaciones:
                op.status = 'failed'
                op.retry_count += 1
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
