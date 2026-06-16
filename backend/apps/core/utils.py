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


# Prefijos de RIF válidos según los manuales SUDEBAN (actualización 09-06-2026):
#   V (Venezolano), E (Extranjero), R (Registro de Firma Personal),
#   C (Comuna y Consejos Comunales), G (Gobierno), J (Jurídico).
# El prefijo "P" fue eliminado de la enumeración de prefijos válidos.
RIF_STANDARD_PREFIXES = ('V', 'E', 'R', 'C', 'G', 'J')

# Longitud máxima del campo 'Identificación Cliente'.
IDENTIFICACION_CLIENTE_MAX_LEN = 20


def parse_rif(rif: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse RIF into prefix and number.

    Returns (prefix, number) for the standard prefixes (V, E, R, C, G, J) with a
    numeric portion of up to 9 digits; otherwise (None, None).
    """
    if rif is None:
        return None, None
    pattern = r'^([VERCGJ])(\d{1,9})$'
    match = re.match(pattern, str(rif).strip().upper())

    if match:
        return match.group(1), match.group(2)
    return None, None


def validate_rif_range(rif_type: str, rif_number: str) -> bool:
    """
    Validate the numeric portion of a RIF.

    Per the SUDEBAN manuals (09-06-2026 update), for the standard prefixes
    (V, E, R, C, G, J) the numeric portion must correspond to a RIF issued by
    SENIAT, i.e. it must be distinct from zero. The previous fixed ranges
    (V: 1..40.000.000; E: 1..1.500.000 / 80.000.000..100.000.000) no longer apply.
    """
    try:
        num = int(rif_number)
    except (ValueError, TypeError):
        return False

    if rif_type in RIF_STANDARD_PREFIXES:
        return num != 0
    return False


def is_valid_identificacion_cliente(value: str) -> bool:
    """
    Validate the 'Identificación Cliente' field per the SUDEBAN manuals.

    - Standard prefix (V, E, R, C, G, J): numeric portion of up to 9 digits,
      distinct from zero (RIF issued by SENIAT).
    - Any other prefix/format: identity document of the client at the regulated
      entity, with a maximum of 20 characters.
    """
    if value is None:
        return False
    v = str(value).strip().upper()
    if not v or v == '0':
        return False
    prefix, number = parse_rif(v)
    if prefix:
        return validate_rif_range(prefix, number)
    return len(v) <= IDENTIFICACION_CLIENTE_MAX_LEN


# Caracteres y símbolos no permitidos en los campos de tipo "TEXTO" según los
# manuales SUDEBAN (Sección IV, "Generación", literal c, y reglas de validación
# de fondo de 'Nombre del Cliente' / 'Código de la Operación').
#
# Nota: se excluyen deliberadamente el punto ".", la coma "," y el guion "-" del
# conjunto prohibido porque forman parte de denominaciones legítimas (por
# ejemplo, razones sociales como "MARIANA C.A.", usada en los propios ejemplos
# de los manuales). El conjunto se centraliza aquí para mantener consistencia
# entre todas las APIs.
NOMBRE_CLIENTE_FORBIDDEN_CHARS = set('@*/+"\'[](){}|\\#$^%&_=÷×;:¿?¡!<>')


def validate_nombre_cliente(value: str) -> str:
    """
    Validate a client name / free TEXT field per the SUDEBAN manuals.

    The value must be distinct from Zero ('0'), empty and Null, and must not
    contain any of the forbidden characters/symbols defined in
    ``NOMBRE_CLIENTE_FORBIDDEN_CHARS``. Returns the trimmed value.
    """
    if value is None:
        raise ValueError("El valor es requerido (no puede ser Null)")
    v = str(value).strip()
    if v == '' or v == '0':
        raise ValueError("El valor no puede ser Cero ('0'), 'Vacío' ni Null")
    found = sorted({c for c in v if c in NOMBRE_CLIENTE_FORBIDDEN_CHARS})
    if found:
        raise ValueError("Contiene caracteres o símbolos no permitidos: " + " ".join(found))
    return v


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
        1048576: "Error hash duplicado en la transacción",
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
        1048576: "Error hash duplicado en la transacción",
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