from django.urls import path
from . import apis

urlpatterns = [
    path('health/', apis.health_check, name='health-check'),
    path('config/', apis.get_config, name='get-config'),
    path('auth/login/', apis.login_view, name='login'),
]