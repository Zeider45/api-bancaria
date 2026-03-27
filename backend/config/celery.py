import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None
from celery import Celery
from celery.schedules import crontab

if load_dotenv is not None:
    this_file = Path(__file__).resolve()
    backend_dir = this_file.parents[1]
    repo_root = this_file.parents[2]
    load_dotenv(backend_dir / '.env', override=False)
    load_dotenv(repo_root / '.env', override=False)

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    os.environ.get('DJANGO_SETTINGS_MODULE', 'config.settings.development'),
)

app = Celery('sib_bridge')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in all apps
app.autodiscover_tasks()

# Scheduled tasks
app.conf.beat_schedule = {
    # API-01: Intervención (manual sugiere ejecución horaria)
    'process_pending_intervencion_transacciones_hourly': {
        'task': 'apps.intervencion_bancaria.tasks.process_pending_transacciones',
        'schedule': crontab(minute=0),
    },
    # API-02: Subasta privada (manual sugiere ejecución cada minuto)
    'process_pending_subasta_solicitudes_every_minute': {
        'task': 'apps.subasta_privada.tasks.process_pending_solicitudes',
        'schedule': crontab(minute='*/1'),
    },
    'retry_failed_subasta_solicitudes_every_10_minutes': {
        'task': 'apps.subasta_privada.tasks.retry_failed_solicitudes',
        'schedule': crontab(minute='*/10'),
    },
    # API-04: Mesa de cambio (ejecución horaria)
    'process_pending_mesa_de_cambio_operaciones_hourly': {
        'task': 'apps.operaciones_mesa_de_cambio.tasks.process_pending_operaciones',
        'schedule': crontab(minute=0),
    },
}
