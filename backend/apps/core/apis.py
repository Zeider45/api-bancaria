import json
import logging
from datetime import datetime

from django.apps import apps as django_apps
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.conf import settings
from ninja import NinjaAPI
from typing import Dict, Any
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.core import selectors
from apps.core.utils import (
    extract_sudeban_error_code,
    extract_sudeban_error_message,
    decode_sudeban_webhook_error,
)
from apps.core.models import SudebanWebhookEvent, TransactionStatus

logger = logging.getLogger(__name__)

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


def _extract_basic_headers(request) -> dict:
    headers: dict = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_') or key in ('CONTENT_TYPE', 'CONTENT_LENGTH'):
            headers[key] = value
    return headers


def _parse_json_body(request):
    try:
        raw = request.body.decode('utf-8', errors='replace') if request.body else ''
        if not raw.strip():
            return True, {}, raw
        return True, json.loads(raw), raw
    except Exception:
        raw = request.body.decode('utf-8', errors='replace') if request.body else ''
        return False, None, raw


# Mapeo API -> (app_label, modelo, [(campo_lookup, (claves_payload,))]).
# Permite enlazar la notificación del webhook con la transacción original.
_WEBHOOK_LINKING = {
    'API-01': ('intervencion_bancaria', 'IntervencionTransaccion', [
        ('codigo_operacion', ('codigoOperacion',)),
        ('codigo_identificacion_intervencion', ('codigoIntervencion', 'codigoIdentificacionIntervencion')),
    ]),
    'API-02': ('subasta_privada', 'SubastaSolicitud', [
        ('codigo_identificacion_subasta', ('codigoSubasta', 'codigoIdentificacionSubasta')),
    ]),
    'API-03': ('resultados_subasta', 'ResultadoSubasta', [
        ('codigo_identificacion_subasta', ('codigoSubasta', 'codigoIdentificacionSubasta')),
    ]),
    'API-04': ('operaciones_mesa_de_cambio', 'OperacionMesaDeCambio', [
        ('codigo_operacion', ('codigoOperacion',)),
    ]),
}


def _lookup_payload_value(payload, keys):
    """Search any of `keys` in the payload and in its nested transaction data."""
    containers = []
    if isinstance(payload, dict):
        containers.append(payload)
        for nested_key in ('transactionData', 'transaction_data', 'datosTransaccion', 'data'):
            nested = payload.get(nested_key)
            if isinstance(nested, dict):
                containers.append(nested)
    for container in containers:
        for key in keys:
            value = container.get(key)
            if value not in (None, '', 0, '0'):
                return str(value).strip()
    return None


def _resolve_transmission_id(payload):
    if not isinstance(payload, dict):
        return None
    for key in ('transmissionId', 'transactionId', 'transmission_id', 'idTransmision'):
        value = payload.get(key)
        if value not in (None, ''):
            return str(value).strip()
    return None


def _link_webhook_to_transaction(api_name, payload, error_code, decoded, error_message):
    """Locate the related transaction and mark it as REJECTED with the error.

    Per the SUDEBAN spec (sección 6.2) a webhook notification is sent only for
    transactions that presented an error, so a matched transaction is moved to
    'rejected' to allow the existing correction/resend flow.
    """
    if not isinstance(payload, dict):
        return None

    config = _WEBHOOK_LINKING.get(api_name)
    if not config:
        return None
    app_label, model_name, lookups = config

    try:
        Model = django_apps.get_model(app_label, model_name)
    except Exception:
        return None

    transaccion = None
    matched_by = None
    for field, keys in lookups:
        value = _lookup_payload_value(payload, keys)
        if not value:
            continue
        transaccion = Model.objects.filter(**{field: value}).order_by('-created_at').first()
        if transaccion:
            matched_by = (field, value)
            break

    if not transaccion:
        return None

    parts = []
    if decoded:
        parts.append('; '.join(decoded))
    if error_message:
        parts.append(error_message)
    detail = ' | '.join(parts) if parts else (
        f"errorCode {error_code}" if error_code is not None else 'Error notificado por SUDEBAN'
    )

    transmission_id = _resolve_transmission_id(payload)

    update_fields = ['status', 'error_code', 'error_detail', 'response_data', 'updated_at']
    transaccion.status = TransactionStatus.REJECTED
    transaccion.error_code = error_code
    transaccion.error_detail = detail
    transaccion.response_data = payload
    if transmission_id and hasattr(transaccion, 'external_id'):
        transaccion.external_id = transmission_id
        update_fields.append('external_id')
    transaccion.save(update_fields=update_fields)

    return {
        'matched': True,
        'app': app_label,
        'model': model_name,
        'id': transaccion.id,
        'matched_by': matched_by[0],
        'matched_value': matched_by[1],
        'transmission_id': transmission_id,
        'status': transaccion.status,
    }


def _handle_sudeban_webhook(request, api_name, api_choice):
    """Shared handler: log the event, decode the error and update the
    corresponding transaction (sections 6.1 - 6.6 of the SUDEBAN manuals)."""
    ok, payload, raw = _parse_json_body(request)

    error_code = extract_sudeban_error_code(payload if ok else raw)
    decoded = decode_sudeban_webhook_error(error_code, api=api_name) if error_code is not None else []
    error_message = extract_sudeban_error_message(payload if ok else raw)

    link_info = None
    if ok:
        try:
            link_info = _link_webhook_to_transaction(api_name, payload, error_code, decoded, error_message)
        except Exception:
            logger.exception("Error al enlazar el webhook %s con la transacción", api_name)

    SudebanWebhookEvent.objects.create(
        api=api_choice,
        path=getattr(request, 'path', '') or '',
        remote_addr=(request.META.get('REMOTE_ADDR') or ''),
        headers=_extract_basic_headers(request),
        raw_body=raw,
        payload=payload if ok else None,
        parse_success=ok,
        error_code=error_code,
        decoded_errors=decoded,
    )

    if not ok:
        return JsonResponse({'detail': 'Invalid JSON body'}, status=400)
    return JsonResponse({
        'success': True,
        'api': api_name,
        'error_code': error_code,
        'error_message': error_message,
        'decoded_errors': decoded,
        'matched_transaction': link_info,
    })


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api01(request):
    """Receive SUDEBAN notifications for API-01 (Intervención Cambiaria)."""
    return _handle_sudeban_webhook(request, 'API-01', SudebanWebhookEvent.ApiName.API01)


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api02(request):
    """Receive SUDEBAN notifications for API-02 (Subasta Privada - Solicitudes)."""
    return _handle_sudeban_webhook(request, 'API-02', SudebanWebhookEvent.ApiName.API02)


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api03(request):
    """Receive SUDEBAN notifications for API-03 (Resultados Subasta)."""
    return _handle_sudeban_webhook(request, 'API-03', SudebanWebhookEvent.ApiName.API03)


@csrf_exempt
@require_http_methods(["POST"])
def sudeban_webhook_api04(request):
    """Receive SUDEBAN notifications for API-04 (Mesa de Cambio)."""
    return _handle_sudeban_webhook(request, 'API-04', SudebanWebhookEvent.ApiName.API04)