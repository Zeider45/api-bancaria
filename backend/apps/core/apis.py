import json
from datetime import datetime

from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.conf import settings
from ninja import NinjaAPI
from typing import Dict, Any
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.core import selectors
from apps.core.utils import extract_sudeban_error_code, decode_sudeban_error

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


@require_http_methods(["GET"])
def get_intervencion_api01_catalogs(request):
    """Return reusable API-01 lookup tables stored in core."""
    return JsonResponse(selectors.get_intervencion_api01_catalogs())


def _parse_json_body(request):
    try:
        raw = request.body.decode('utf-8') if request.body else ''
        if not raw:
            return True, {}
        return True, json.loads(raw)
    except Exception:
        return False, None


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api01(request):
    """Receive SUDEBAN notifications for API-01 (Intervención Cambiaria)."""
    ok, payload = _parse_json_body(request)
    if not ok:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    error_code = extract_sudeban_error_code(payload)
    decoded = decode_sudeban_error(error_code, api='API-01') if error_code is not None else []

    return JsonResponse({'success': True, 'api': 'API-01', 'error_code': error_code, 'decoded_errors': decoded})


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api02(request):
    """Receive SUDEBAN notifications for API-02 (Subasta Privada - Solicitudes)."""
    ok, payload = _parse_json_body(request)
    if not ok:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    error_code = extract_sudeban_error_code(payload)
    decoded = decode_sudeban_error(error_code, api='API-02') if error_code is not None else []

    return JsonResponse({'success': True, 'api': 'API-02', 'error_code': error_code, 'decoded_errors': decoded})


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api03(request):
    """Receive SUDEBAN notifications for API-03 (Resultados Subasta)."""
    ok, payload = _parse_json_body(request)
    if not ok:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    error_code = extract_sudeban_error_code(payload)
    decoded = decode_sudeban_error(error_code, api='API-03') if error_code is not None else []

    return JsonResponse({'success': True, 'api': 'API-03', 'error_code': error_code, 'decoded_errors': decoded})


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api04(request):
    """Receive SUDEBAN notifications for API-04 (Mesa de Cambio)."""
    ok, payload = _parse_json_body(request)
    if not ok:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)

    error_code = extract_sudeban_error_code(payload)
    decoded = decode_sudeban_error(error_code, api='API-04') if error_code is not None else []

    return JsonResponse({'success': True, 'api': 'API-04', 'error_code': error_code, 'decoded_errors': decoded})