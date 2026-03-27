import re
from ninja import Schema
from pydantic import field_validator, Field, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from django.utils import timezone
from apps.core.utils import parse_rif
from apps.core import selectors as core_selectors


DecimalField = condecimal(max_digits=20, decimal_places=4)

VALID_ACCOUNT_PREFIXES = re.compile(r'^\d{20}$')


class OperacionMesaDeCambioInput(Schema):
    """
    Input schema for receiving mesa de cambio transactions from internal systems.
    """

    # Ente Supervisado
    identificacion_ente_supervisado: Optional[str] = Field(None, max_length=99)

    # Datos del pacto
    tipo_pacto: str = Field(..., max_length=99)
    moneda: int
    fecha_pacto: datetime

    # Montos
    monto_divisa: DecimalField
    tipo_cambio_bs: DecimalField
    contravalor_bs: Optional[DecimalField] = None

    # Cliente Oferente
    identificacion_cliente_oferente: str = Field(..., max_length=20)
    nombre_cliente_oferente: str = Field(..., min_length=1, max_length=100)
    actividad_economica_cliente_oferente: str = Field(..., max_length=99)
    codigo_cuenta_moneda_nacional_oferente: str = Field(..., max_length=20)
    tipo_cuenta_moneda_nacional_cliente_oferente: int
    codigo_cuenta_moneda_extranjera_oferente: str = Field(..., max_length=20)
    tipo_cuenta_moneda_extranjera_cliente_oferente: int
    origen_fondos: int
    medio_pago_oferente: int

    # Cliente Demandante
    identificacion_cliente_demandante: str = Field(..., max_length=20)
    nombre_cliente_demandante: str = Field(..., min_length=1, max_length=100)
    actividad_economica_cliente_demandante: str = Field(..., max_length=99)
    codigo_cuenta_moneda_nacional_demandante: str = Field(..., max_length=20)
    tipo_cuenta_moneda_nacional_cliente_demandante: int
    codigo_cuenta_moneda_extranjera_demandante: str = Field(..., max_length=20)
    tipo_cuenta_moneda_extranjera_cliente_demandante: int
    destino_fondos: int
    medio_pago_demandante: int

    @field_validator('identificacion_ente_supervisado')
    def validate_ente_supervisado(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_ente_supervisado(v):
            raise ValueError('Identificación Ente Supervisado inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('moneda')
    def validate_moneda(cls, v):
        if v is None:
            raise ValueError('Moneda es requerida')
        if not core_selectors.is_valid_moneda(v):
            raise ValueError('Moneda inválida (no existe en el catálogo)')
        return int(v)

    @field_validator('actividad_economica_cliente_oferente')
    def validate_actividad_economica_oferente(cls, v):
        if not core_selectors.is_valid_actividad_economica(v):
            raise ValueError('Actividad Económica Cliente Oferente inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('actividad_economica_cliente_demandante')
    def validate_actividad_economica_demandante(cls, v):
        if not core_selectors.is_valid_actividad_economica(v):
            raise ValueError('Actividad Económica Cliente Demandante inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('origen_fondos')
    def validate_origen_fondos(cls, v):
        if v is None:
            raise ValueError('Origen Fondos es requerido')
        if not core_selectors.is_valid_destino_fondos(v):
            raise ValueError('Origen Fondos inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('destino_fondos')
    def validate_destino_fondos(cls, v):
        if v is None:
            raise ValueError('Destino Fondos es requerido')
        if not core_selectors.is_valid_destino_fondos(v):
            raise ValueError('Destino Fondos inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('medio_pago_oferente')
    def validate_medio_pago_oferente(cls, v):
        if v is None:
            raise ValueError('Medio Pago Oferente es requerido')
        if not core_selectors.is_valid_medio_pago(v):
            raise ValueError('Medio Pago Oferente inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('medio_pago_demandante')
    def validate_medio_pago_demandante(cls, v):
        if v is None:
            raise ValueError('Medio Pago Demandante es requerido')
        if not core_selectors.is_valid_medio_pago(v):
            raise ValueError('Medio Pago Demandante inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('fecha_pacto')
    def validate_fecha_pacto(cls, v):
        """Fecha Pacto must be >= the current transmission date/time."""
        now = timezone.now()
        # Support both aware and naive datetimes for comparison
        v_comparable = v if v.tzinfo else timezone.make_aware(v)
        if v_comparable < now:
            raise ValueError('Fecha Pacto debe ser mayor o igual a la fecha de transmisión')
        return v

    @field_validator('identificacion_cliente_oferente')
    def validate_id_oferente(cls, v):
        """Validate identification format: prefix (V,E,P,R,C,G,J) followed by digits."""
        rif_type, _ = parse_rif(v)
        if not rif_type:
            raise ValueError(
                'Identificación Cliente Oferente inválida. '
                'Debe tener prefijo V, E, P, R, C, G o J seguido de dígitos.'
            )
        return v.upper()

    @field_validator('identificacion_cliente_demandante')
    def validate_id_demandante(cls, v):
        """Validate identification format: prefix (V,E,P,R,C,G,J) followed by digits."""
        rif_type, _ = parse_rif(v)
        if not rif_type:
            raise ValueError(
                'Identificación Cliente Demandante inválida. '
                'Debe tener prefijo V, E, P, R, C, G o J seguido de dígitos.'
            )
        return v.upper()

    @field_validator('codigo_cuenta_moneda_nacional_oferente')
    def validate_cuenta_nacional_oferente(cls, v):
        """Account code must be exactly 20 numeric digits."""
        if not VALID_ACCOUNT_PREFIXES.match(v):
            raise ValueError('Código Cuenta Moneda Nacional Oferente debe ser un número de exactamente 20 dígitos')
        return v

    @field_validator('codigo_cuenta_moneda_extranjera_oferente')
    def validate_cuenta_extranjera_oferente(cls, v):
        """Account code must be exactly 20 numeric digits."""
        if not VALID_ACCOUNT_PREFIXES.match(v):
            raise ValueError('Código Cuenta Moneda Extranjera Oferente debe ser un número de exactamente 20 dígitos')
        return v

    @field_validator('tipo_cuenta_moneda_nacional_cliente_oferente')
    def validate_tipo_cuenta_nacional_oferente(cls, v):
        """Tipo cuenta moneda nacional must be 8, 9 or 10."""
        if v not in (8, 9, 10):
            raise ValueError('Tipo Cuenta Moneda Nacional Cliente Oferente debe ser 8, 9 o 10')
        return v

    @field_validator('tipo_cuenta_moneda_extranjera_cliente_oferente')
    def validate_tipo_cuenta_extranjera_oferente(cls, v):
        """Tipo cuenta moneda extranjera must be 31 or 32."""
        if v not in (31, 32):
            raise ValueError('Tipo Cuenta Moneda Extranjera Cliente Oferente debe ser 31 o 32')
        return v

    @field_validator('codigo_cuenta_moneda_nacional_demandante')
    def validate_cuenta_nacional_demandante(cls, v):
        """Account code must be exactly 20 numeric digits."""
        if not VALID_ACCOUNT_PREFIXES.match(v):
            raise ValueError('Código Cuenta Moneda Nacional Demandante debe ser un número de exactamente 20 dígitos')
        return v

    @field_validator('codigo_cuenta_moneda_extranjera_demandante')
    def validate_cuenta_extranjera_demandante(cls, v):
        """Account code must be exactly 20 numeric digits."""
        if not VALID_ACCOUNT_PREFIXES.match(v):
            raise ValueError('Código Cuenta Moneda Extranjera Demandante debe ser un número de exactamente 20 dígitos')
        return v

    @field_validator('tipo_cuenta_moneda_nacional_cliente_demandante')
    def validate_tipo_cuenta_nacional_demandante(cls, v):
        """Validate tipo de cuenta (Destino) per SUDEBAN manual codes.

        The operational manual uses numeric codes and may include values beyond
        (8, 9, 10) for the Destino side.
        """
        if v is None or v <= 0:
            raise ValueError('Tipo Cuenta Moneda Nacional Cliente Demandante debe ser un entero mayor que 0')
        return v

    @field_validator('tipo_cuenta_moneda_extranjera_cliente_demandante')
    def validate_tipo_cuenta_extranjera_demandante(cls, v):
        """Validate tipo de cuenta extranjera (Destino) per SUDEBAN manual codes."""
        if v is None or v <= 0:
            raise ValueError('Tipo Cuenta Moneda Extranjera Cliente Demandante debe ser un entero mayor que 0')
        return v


class OperacionMesaDeCambioBatchInput(Schema):
    """Schema for receiving multiple mesa de cambio transactions."""
    transacciones: List[OperacionMesaDeCambioInput]
    webhook_url: Optional[str] = None


class OperacionMesaDeCambioOutput(Schema):
    """Output schema for mesa de cambio transaction data."""
    id: int
    identificacion_ente_supervisado: str
    tipo_pacto: str
    moneda: int
    fecha_pacto: datetime
    monto_divisa: Decimal
    tipo_cambio_bs: Decimal
    contravalor_bs: Decimal
    identificacion_cliente_oferente: str
    nombre_cliente_oferente: str
    identificacion_cliente_demandante: str
    nombre_cliente_demandante: str
    status: str
    error_code: Optional[int] = None
    error_detail: Optional[str] = None
    created_at: datetime


class OperacionMesaDeCambioCorreccionInput(Schema):
    """Schema for correcting rejected mesa de cambio transactions."""
    tipo_pacto: Optional[str] = None
    moneda: Optional[int] = None
    monto_divisa: Optional[Decimal] = None
    tipo_cambio_bs: Optional[Decimal] = None
    contravalor_bs: Optional[Decimal] = None
    nombre_cliente_oferente: Optional[str] = None
    actividad_economica_cliente_oferente: Optional[str] = None
    codigo_cuenta_moneda_nacional_oferente: Optional[str] = None
    tipo_cuenta_moneda_nacional_cliente_oferente: Optional[int] = None
    codigo_cuenta_moneda_extranjera_oferente: Optional[str] = None
    tipo_cuenta_moneda_extranjera_cliente_oferente: Optional[int] = None
    origen_fondos: Optional[int] = None
    medio_pago_oferente: Optional[int] = None
    nombre_cliente_demandante: Optional[str] = None
    actividad_economica_cliente_demandante: Optional[str] = None
    codigo_cuenta_moneda_nacional_demandante: Optional[str] = None
    tipo_cuenta_moneda_nacional_cliente_demandante: Optional[int] = None
    codigo_cuenta_moneda_extranjera_demandante: Optional[str] = None
    tipo_cuenta_moneda_extranjera_cliente_demandante: Optional[int] = None
    destino_fondos: Optional[int] = None
    medio_pago_demandante: Optional[int] = None

    @field_validator('moneda')
    def validate_moneda(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_moneda(v):
            raise ValueError('Moneda inválida (no existe en el catálogo)')
        return int(v)

    @field_validator('actividad_economica_cliente_oferente')
    def validate_actividad_economica_oferente(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_actividad_economica(v):
            raise ValueError('Actividad Económica Cliente Oferente inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('actividad_economica_cliente_demandante')
    def validate_actividad_economica_demandante(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_actividad_economica(v):
            raise ValueError('Actividad Económica Cliente Demandante inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('origen_fondos')
    def validate_origen_fondos(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_destino_fondos(v):
            raise ValueError('Origen Fondos inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('destino_fondos')
    def validate_destino_fondos(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_destino_fondos(v):
            raise ValueError('Destino Fondos inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('medio_pago_oferente')
    def validate_medio_pago_oferente(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_medio_pago(v):
            raise ValueError('Medio Pago Oferente inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('medio_pago_demandante')
    def validate_medio_pago_demandante(cls, v):
        if v is None:
            return v
        if not core_selectors.is_valid_medio_pago(v):
            raise ValueError('Medio Pago Demandante inválido (no existe en el catálogo)')
        return int(v)
