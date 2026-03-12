import logging
from typing import Dict, Any

from django.db import transaction as db_transaction

from .models import MesaDeCambioOperacion
from .serializers import MesaDeCambioOperacionInput, MesaDeCambioCorreccionInput

logger = logging.getLogger(__name__)


def create_operacion(data: MesaDeCambioOperacionInput) -> MesaDeCambioOperacion:
    """
    Create a new mesa de cambio operation
    """
    with db_transaction.atomic():
        if MesaDeCambioOperacion.objects.filter(
            codigo_identificacion_operacion=data.codigo_identificacion_operacion
        ).exists():
            raise ValueError(
                f"Operation with code {data.codigo_identificacion_operacion} already exists"
            )

        contravalor = data.contravalor_bs
        if not contravalor and data.monto_divisa and data.tipo_cambio_bs:
            contravalor = data.monto_divisa * data.tipo_cambio_bs

        operacion = MesaDeCambioOperacion.objects.create(
            codigo_ente_supervisado=data.codigo_ente_supervisado,
            codigo_identificacion_operacion=data.codigo_identificacion_operacion,
            fecha_operacion=data.fecha_operacion,
            identificacion_cliente=data.identificacion_cliente.upper(),
            nombre_cliente=data.nombre_cliente,
            actividad_economica_cliente=data.actividad_economica_cliente,
            moneda=data.moneda,
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

        logger.info(f"Created mesa de cambio operation: {operacion.codigo_identificacion_operacion}")
        return operacion


def correct_operacion(operacion_id: int, data: MesaDeCambioCorreccionInput) -> MesaDeCambioOperacion:
    """
    Apply corrections to a rejected operation
    """
    with db_transaction.atomic():
        operacion = MesaDeCambioOperacion.objects.get(id=operacion_id)

        if operacion.status != 'rejected':
            raise ValueError("Only rejected operations can be corrected")

        update_fields = []
        for field, value in data.dict(exclude_unset=True).items():
            if value is not None and hasattr(operacion, field):
                setattr(operacion, field, value)
                update_fields.append(field)

        operacion.status = 'pending'
        operacion.error_code = None
        operacion.error_detail = None
        operacion.retry_count = 0
        update_fields.extend(['status', 'error_code', 'error_detail', 'retry_count'])

        operacion.save(update_fields=update_fields)

        logger.info(f"Corrected mesa de cambio operation {operacion_id}")
        return operacion
