import logging
from celery import shared_task
from django.conf import settings
from datetime import datetime
from typing import List

from .selectors import list_solicitudes_for_batch
from .services import send_to_sudeban, validate_solicitud_for_sudeban
from .models import SubastaSolicitud

logger = logging.getLogger(__name__)


@shared_task
def process_pending_solicitudes():
    """
    Celery task to process and send pending subasta requests
    Runs in real-time as per manual (every minute)
    """
    logger.info("Starting to process pending subasta requests")
    
    # Get pending requests
    solicitudes = list(list_solicitudes_for_batch(max_records=100))
    
    if not solicitudes:
        logger.info("No pending requests to process")
        return {'processed': 0}
    
    # First, validate each request
    valid_solicitudes = []
    invalid_solicitudes = []
    
    for s in solicitudes:
        is_valid, errors = validate_solicitud_for_sudeban(s)
        if is_valid:
            valid_solicitudes.append(s)
        else:
            # Mark as rejected with errors
            s.status = 'rejected'
            s.error_detail = '; '.join(errors)
            s.save()
            invalid_solicitudes.append(s.id)
    
    logger.info(f"Valid: {len(valid_solicitudes)}, Invalid: {len(invalid_solicitudes)}")
    
    if not valid_solicitudes:
        return {
            'processed': 0,
            'invalid': len(invalid_solicitudes)
        }
    
    # Send valid requests to SUDEBAN
    result = send_to_sudeban(
        valid_solicitudes,
        webhook_url=settings.SUDEBAN_WEBHOOK_URL
    )
    
    if result['success']:
        logger.info(f"Successfully sent {result['count']} subasta requests")
        return {
            'processed': result['count'],
            'invalid': len(invalid_solicitudes)
        }
    else:
        logger.error(f"Failed to send batch: {result.get('detail')}")
        # Mark all as failed
        for s in valid_solicitudes:
            s.status = 'failed'
            s.save()
        
        return {
            'processed': 0,
            'failed': len(valid_solicitudes),
            'invalid': len(invalid_solicitudes),
            'error': result.get('detail')
        }


@shared_task
def process_single_solicitud(solicitud_id: int):
    """
    Process a single subasta request (for retries or corrections)
    """
    try:
        solicitud = SubastaSolicitud.objects.get(id=solicitud_id)
    except SubastaSolicitud.DoesNotExist:
        logger.error(f"Subasta request {solicitud_id} not found")
        return {'error': 'Request not found'}
    
    # Validate
    is_valid, errors = validate_solicitud_for_sudeban(solicitud)
    if not is_valid:
        solicitud.status = 'rejected'
        solicitud.error_detail = '; '.join(errors)
        solicitud.save()
        return {
            'success': False,
            'errors': errors
        }
    
    # Send
    result = send_to_sudeban([solicitud])
    
    if result['success']:
        solicitud.status = 'sent'
        solicitud.last_sent_at = datetime.now()
        solicitud.save()
        return {'success': True}
    else:
        solicitud.status = 'failed'
        solicitud.retry_count += 1
        solicitud.error_detail = result.get('detail')
        solicitud.save()
        return {
            'success': False,
            'error': result.get('detail')
        }


@shared_task
def retry_failed_solicitudes():
    """
    Retry failed subasta requests (max 5 times)
    """
    failed = SubastaSolicitud.objects.filter(
        status='failed',
        retry_count__lt=5
    )[:50]
    
    for solicitud in failed:
        process_single_solicitud.delay(solicitud.id)
    
    logger.info(f"Queued {len(failed)} failed requests for retry")
    return {'retried': len(failed)}