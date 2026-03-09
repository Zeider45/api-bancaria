import logging
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .selectors import list_operaciones_for_batch
from .services import send_to_sudeban, validate_operacion_for_sudeban
from .models import OperacionMesaDeCambio

logger = logging.getLogger(__name__)


@shared_task
def process_pending_operaciones():
    """
    Celery task to validate and send pending mesa de cambio transactions in batches.
    Intended to run periodically (e.g., every hour).
    """
    logger.info("Starting to process pending mesa de cambio transactions")

    operaciones = list(list_operaciones_for_batch(max_records=1000))

    if not operaciones:
        logger.info("No pending mesa de cambio transactions to process")
        return {'processed': 0}

    valid_operaciones = []
    invalid_ids = []

    for op in operaciones:
        is_valid, errors = validate_operacion_for_sudeban(op)
        if is_valid:
            valid_operaciones.append(op)
        else:
            op.status = 'rejected'
            op.error_detail = '; '.join(errors)
            op.save()
            invalid_ids.append(op.id)

    logger.info(f"Valid: {len(valid_operaciones)}, Invalid: {len(invalid_ids)}")

    if not valid_operaciones:
        return {
            'processed': 0,
            'invalid': len(invalid_ids),
        }

    result = send_to_sudeban(
        valid_operaciones,
        webhook_url=getattr(settings, 'SUDEBAN_WEBHOOK_URL', None),
    )

    if result['success']:
        logger.info(f"Successfully sent {result['count']} mesa de cambio transactions")
        return {
            'processed': result['count'],
            'invalid': len(invalid_ids),
        }
    else:
        logger.error(f"Failed to send mesa de cambio batch: {result.get('detail')}")
        for op in valid_operaciones:
            op.status = 'failed'
            op.save()

        return {
            'processed': 0,
            'failed': len(valid_operaciones),
            'invalid': len(invalid_ids),
            'error': result.get('detail'),
        }


@shared_task
def process_single_operacion(operacion_id: int):
    """
    Process a single mesa de cambio transaction (for retries or after correction).
    """
    try:
        operacion = OperacionMesaDeCambio.objects.get(id=operacion_id)
    except OperacionMesaDeCambio.DoesNotExist:
        logger.error(f"Mesa de cambio transaction {operacion_id} not found")
        return {'error': 'Transaction not found'}

    is_valid, errors = validate_operacion_for_sudeban(operacion)
    if not is_valid:
        operacion.status = 'rejected'
        operacion.error_detail = '; '.join(errors)
        operacion.save()
        return {'success': False, 'errors': errors}

    result = send_to_sudeban([operacion])

    if result['success']:
        operacion.status = 'sent'
        operacion.last_sent_at = timezone.now()
        operacion.save()
        return {'success': True}
    else:
        operacion.status = 'failed'
        operacion.retry_count += 1
        operacion.save()
        return {
            'success': False,
            'error': result.get('detail'),
        }
