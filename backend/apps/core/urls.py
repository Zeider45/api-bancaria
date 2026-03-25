from django.urls import path
from . import apis

urlpatterns = [
    path('health/', apis.health_check, name='health-check'),
    path('config/', apis.get_config, name='get-config'),
    path('auth/login/', apis.login_view, name='login'),
    path('catalogs/intervencion-api01/', apis.get_intervencion_api01_catalogs, name='intervencion-api01-catalogs'),
    path('webhooks/api01/', apis.sudeban_webhook_api01, name='sudeban-webhook-api01'),
    path('webhooks/api02/', apis.sudeban_webhook_api02, name='sudeban-webhook-api02'),
    path('webhooks/api03/', apis.sudeban_webhook_api03, name='sudeban-webhook-api03'),
    path('webhooks/api04/', apis.sudeban_webhook_api04, name='sudeban-webhook-api04'),
]