import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('sib_bridge')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    # Intervención Cambiaria - cada hora (as per manual)
    'process-intervencion-hourly': {
        'task': 'apps.intervencion_bancaria.tasks.process_pending_transacciones',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
    
    # Subasta Privada - cada minuto (tiempo real as per manual)
    'process-subasta-realtime': {
        'task': 'apps.subasta_privada.tasks.process_pending_solicitudes',
        'schedule': crontab(minute='*'),  # Every minute
    },
    
    # Retry failed - cada 30 minutos
    'retry-failed-subasta': {
        'task': 'apps.subasta_privada.tasks.retry_failed_solicitudes',
        'schedule': crontab(minute='*/30'),
    },

    # Mesa de Cambio - cada hora
    'process-mesa-de-cambio-hourly': {
        'task': 'apps.operaciones_mesa_de_cambio.tasks.process_pending_operaciones',
        'schedule': crontab(minute=0),  # Every hour at minute 0
    },
}