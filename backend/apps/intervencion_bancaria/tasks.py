import logging
from celery import shared_task
from django.conf import settings
from datetime import datetime
from typing import List

from .selectors import list_transacciones_for_batch
from .services import send_to_sudeban, validate_transaction_for_sudeban
from .models import IntervencionTransaccion

logger = logging.getLogger(__name__)


@shared_task
def process_pending_transacciones():
    """
    Celery task to process and send pending transactions in batches
    Runs every hour as per manual
    """
    logger.info("Starting to process pending intervencion transactions")
    
    # Get pending transactions
    transacciones = list(list_transacciones_for_batch(max_records=1000))
    
    if not transacciones:
        logger.info("No pending transactions to process")
        return {'processed': 0}
    
    # First, validate each transaction
    valid_transacciones = []
    invalid_transacciones = []
    
    for t in transacciones:
        is_valid, errors = validate_transaction_for_sudeban(t)
        if is_valid:
            valid_transacciones.append(t)
        else:
            # Mark as rejected with errors
            t.status = 'rejected'
            t.error_detail = '; '.join(errors)
            t.save()
            invalid_transacciones.append(t.id)
    
    logger.info(f"Valid: {len(valid_transacciones)}, Invalid: {len(invalid_transacciones)}")
    
    if not valid_transacciones:
        return {
            'processed': 0,
            'invalid': len(invalid_transacciones)
        }
    
    # Send valid transactions to SUDEBAN
    result = send_to_sudeban(
        valid_transacciones,
        webhook_url=getattr(settings, 'SUDEBAN_WEBHOOK_URL_API01', getattr(settings, 'SUDEBAN_WEBHOOK_URL', None))
    )
    
    if result['success']:
        logger.info(f"Successfully sent {result['count']} transactions")
        return {
            'processed': result['count'],
            'invalid': len(invalid_transacciones)
        }
    else:
        logger.error(f"Failed to send batch: {result.get('detail')}")
        # Mark all as failed
        for t in valid_transacciones:
            t.status = 'failed'
            t.save()
        
        return {
            'processed': 0,
            'failed': len(valid_transacciones),
            'invalid': len(invalid_transacciones),
            'error': result.get('detail')
        }


@shared_task
def process_single_transaccion(transaccion_id: int):
    """
    Process a single transaction (for retries or corrections)
    """
    try:
        transaccion = IntervencionTransaccion.objects.get(id=transaccion_id)
    except IntervencionTransaccion.DoesNotExist:
        logger.error(f"Transaction {transaccion_id} not found")
        return {'error': 'Transaction not found'}
    
    # Validate
    is_valid, errors = validate_transaction_for_sudeban(transaccion)
    if not is_valid:
        transaccion.status = 'rejected'
        transaccion.error_detail = '; '.join(errors)
        transaccion.save()
        return {
            'success': False,
            'errors': errors
        }
    
    # Send
    result = send_to_sudeban(
        [transaccion],
        webhook_url=getattr(settings, 'SUDEBAN_WEBHOOK_URL_API01', getattr(settings, 'SUDEBAN_WEBHOOK_URL', None)),
    )
    
    if result['success']:
        transaccion.status = 'sent'
        transaccion.last_sent_at = datetime.now()
        transaccion.save()
        return {'success': True}
    else:
        transaccion.status = 'failed'
        transaccion.retry_count += 1
        transaccion.save()
        return {
            'success': False,
            'error': result.get('detail')
        }