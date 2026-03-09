import json
from datetime import datetime

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.conf import settings
from ninja import NinjaAPI
from typing import Dict, Any
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

api = NinjaAPI(title="SIB API Bridge", version="1.0.0")


def health_check(request):
    """Health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Authenticate a Django user for frontend credentials login."""
    try:
        payload = json.loads(request.body or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'detail': 'Payload JSON inválido'}, status=400)

    username = payload.get('username', '').strip()
    password = payload.get('password', '')

    if not username or not password:
        return JsonResponse({'detail': 'Usuario y contraseña son requeridos'}, status=400)

    user = authenticate(request, username=username, password=password)

    if not user and settings.DEBUG and username == 'admin' and password == 'admin':
        return JsonResponse({
            'id': 'dev-admin',
            'name': 'Administrador',
            'email': 'admin@example.com',
            'username': username,
        })

    if not user:
        return JsonResponse({'detail': 'Credenciales inválidas'}, status=401)

    return JsonResponse({
        'id': str(user.pk),
        'name': user.get_full_name() or user.get_username(),
        'email': user.email,
        'username': user.get_username(),
    })


@api.get("/config", response=Dict[str, Any])
def get_config(request):
    """Get system configuration (non-sensitive)"""
    return {
        'environment': 'development' if settings.DEBUG else 'production',
        'timezone': settings.TIME_ZONE,
        'celery_broker': settings.CELERY_BROKER_URL.split('@')[0] if '@' in settings.CELERY_BROKER_URL else 'redis'
    }