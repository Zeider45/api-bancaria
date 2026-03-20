from django.urls import path
from . import apis

urlpatterns = [
    path('health/', apis.health_check, name='health-check'),
    path('config/', apis.get_config, name='get-config'),
    path('auth/login/', apis.login_view, name='login'),
    path('catalogs/intervencion-api01/', apis.get_intervencion_api01_catalogs, name='intervencion-api01-catalogs'),
]