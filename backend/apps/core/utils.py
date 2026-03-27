import re
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)


def format_date_for_sudeban(dt: datetime) -> str:
    """
    Format datetime to SUDEBAN required format: AAAA-MM-DDTHH:MM:SS.sss
    """
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]


def parse_sudeban_date(date_str: str) -> Optional[datetime]:
    """
    Parse SUDEBAN date format back to datetime
    """
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%f')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            logger.error(f"Invalid date format: {date_str}")
            return None


def format_amount(amount: Decimal, decimal_places: int = 4) -> str:
    """
    Format amount with required decimal places
    """
    return str(amount.quantize(Decimal(f'0.{"0" * decimal_places}'), rounding=ROUND_HALF_UP))


def parse_rif(rif: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse RIF into prefix and number
    Returns (prefix, number)
    """
    pattern = r'^([VEJPGCR])(\d+)$'
    match = re.match(pattern, rif.strip().upper())
    
    if match:
        return match.group(1), match.group(2)
    return None, None


def validate_rif_range(rif_type: str, rif_number: str) -> bool:
    """
    Validate RIF number ranges based on type
    """
    try:
        num = int(rif_number)
        
        if rif_type == 'V':  # Venezolano
            return 1 <= num <= 40000000
        elif rif_type == 'E':  # Extranjero
            return (1 <= num <= 1500000) or (80000000 <= num <= 100000000)
        elif rif_type in ['J', 'G', 'C', 'R']:  # Legal entities
            return True  # Format validated by SENIAT, accept all
        return False
    except ValueError:
        return False


def build_error_response(error_code: int, detail: str) -> Dict[str, Any]:
    """
    Build standardized error response
    """
    return {
        'success': False,
        'error_code': error_code,
        'detail': detail
    }


def get_sudeban_ente_supervisado() -> str:
    """Return the supervised entity code from settings.

    This is the single source of truth for the 'ente supervisado' value.
    """
    from django.conf import settings
    from apps.core import selectors as core_selectors

    ente = getattr(settings, 'SUDEBAN_ID_ENTIDAD_BANCARIA', None)
    if ente is None or str(ente).strip() == '':
        raise ValueError('SUDEBAN_ID_ENTIDAD_BANCARIA no está configurado')

    ente_str = str(ente).strip()
    if not core_selectors.is_valid_ente_supervisado(ente_str):
        raise ValueError('SUDEBAN_ID_ENTIDAD_BANCARIA inválido (no existe en el catálogo)')

    return ente_str


_SUDEBAN_ERROR_MESSAGES_DEFAULT: Dict[int, str] = {
        1: "Validación del campo 'Moneda'",
        2: "Validación de los campos: 'Tipo de Pacto', 'Tipo Operación'",
        4: "Validación del campo 'Actividad Económica' cliente origen de los fondos",
        8: "Validación del campo 'Origen de los Fondos'",
        16: "Validación del campo 'Medio de Pago' del cliente origen de los fondos",
        32: "Validación del campo 'Actividad Económica' cliente destino de los fondos",
        64: "Validación del campo 'Destino de los Fondos'",
        128: "Validación del campo 'Medio de Pago' al cliente destino de los fondos",
        256: "Validación del campo 'Tipo de Cuenta'. Aplica para Cuenta en moneda nacional y moneda extranjera.",
        512: "Validación del campo 'Identificación Ente Supervisado'",
        1024: "Validación del campo 'Tipo Transferencia'",
        2048: "Validación del campo 'Instrumento Transacción' del cliente origen",
        4096: "Validación del campo 'Instrumento Transacción' del cliente destino",
        8192: "Validación de los campos: 'Tipo de Pacto', 'Tipo Operación' en los casos donde la operación origen y destino no corresponde",
        16384: "Validación de los campos: 'Tipo de Pacto', 'Tipo Operación' en los casos donde la operación origen y destino no corresponde",
        65536: "Error en datos de identificación de Código Cuenta Cliente, Teléfono Pago Móvil Origen o en Teléfono Pago Móvil Contraparte",
        131072: "Validación del campo 'Tipo Transacción'",
        524288: "Error de validación del Estatus de Verificación",
        4194304: "Duplicidad en la identificación de la transacción",
        # Date-fields validation varies per API; overridden in per-API tables.
        8388608: "Validación de los campos: 'Fecha Intervención', 'Fecha Operación Cliente'",
        33554432: "Validación del Campo 'Contravalor Bs', 'Contravalor Final Bs'",
}

# Optional API-specific overrides. If an API key is missing, the default table is used.
_SUDEBAN_ERROR_MESSAGES_BY_API: Dict[str, Dict[int, str]] = {
    # API-01: Intervención Cambiaria a través del BCV
    'API-01': {
        **_SUDEBAN_ERROR_MESSAGES_DEFAULT,
        8388608: "Validación de los campos: 'Fecha Intervención', 'Fecha Operación Cliente'",
    },
    # API-02: Libro de órdenes Subasta Privada
    'API-02': {
        **_SUDEBAN_ERROR_MESSAGES_DEFAULT,
        8388608: "Validación de los campos: 'Fecha Subasta', 'Fecha Solicitud'",
    },
    # API-03: Resultados de la Subasta Privada
    'API-03': {
        **_SUDEBAN_ERROR_MESSAGES_DEFAULT,
        8388608: "Validación de los campos: 'Fecha Subasta', 'Fecha Solicitud'",
    },
    # API-04: Operaciones a través de Mesas de Cambio
    'API-04': {
        **_SUDEBAN_ERROR_MESSAGES_DEFAULT,
        8388608: "Validación de los campos: 'Fecha Pacto'",
    },
}


def _iter_set_bits(value: int):
    remaining = int(value)
    while remaining:
        lowest = remaining & -remaining
        yield int(lowest)
        remaining -= lowest


def decode_sudeban_error(error_code: int, api: Optional[str] = None) -> list:
    """Decode SUDEBAN error codes (bitmask) into a list of human-friendly messages.

    `api` allows selecting an API-specific table (API-01..API-04). If not
    provided, or if no specific table is found, the default table is used.
    """

    if error_code is None:
        return []

    try:
        error_code_int = int(error_code)
    except Exception:
        return [f"Error desconocido: {error_code}"]

    if error_code_int == 0:
        return []

    table = _SUDEBAN_ERROR_MESSAGES_BY_API.get(api) or _SUDEBAN_ERROR_MESSAGES_DEFAULT
    messages: list[str] = []

    for bit in sorted(table.keys()):
        if error_code_int & bit:
            messages.append(table[bit])

    known_mask = 0
    for bit in table.keys():
        known_mask |= bit

    unknown_part = error_code_int & ~known_mask
    if unknown_part:
        unknown_bits = list(_iter_set_bits(unknown_part))
        messages.append(f"Códigos desconocidos: {', '.join(map(str, unknown_bits))}")

    return messages if messages else [f"Error desconocido: {error_code_int}"]


def extract_sudeban_error_code(detail: Any) -> Optional[int]:
    """Best-effort extraction of SUDEBAN error codes.

    SUDEBAN error payloads may come as strings, dicts, or nested dicts.
    We look for common keys like `errorCode` and variants.
    """

    def _to_int(value: Any) -> Optional[int]:
        if value is None:
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            stripped = value.strip()
            if stripped.isdigit():
                try:
                    return int(stripped)
                except ValueError:
                    return None
        return None

    def _search(obj: Any, depth: int = 0) -> Optional[int]:
        if depth > 3:
            return None
        if isinstance(obj, dict):
            for key in (
                'errorCode',
                'error_code',
                'codigoError',
                'codigo_error',
                'codError',
            ):
                if key in obj:
                    found = _to_int(obj.get(key))
                    if found is not None:
                        return found

            for value in obj.values():
                found = _search(value, depth + 1)
                if found is not None:
                    return found

        if isinstance(obj, list):
            for item in obj[:10]:
                found = _search(item, depth + 1)
                if found is not None:
                    return found

        if isinstance(obj, str):
            # Sometimes it's a JSON string.
            try:
                parsed = json.loads(obj)
            except Exception:
                return None
            return _search(parsed, depth + 1)

        return None

    return _search(detail)