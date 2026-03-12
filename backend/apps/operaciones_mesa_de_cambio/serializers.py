import re
from ninja import Schema
from pydantic import field_validator, Field, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from django.utils import timezone
from apps.core.utils import parse_rif


DecimalField = condecimal(max_digits=20, decimal_places=4)

VALID_ACCOUNT_PREFIXES = re.compile(r'^\d{20}$')


class OperacionMesaDeCambioInput(Schema):
    """
    Input schema for receiving mesa de cambio transactions from internal systems.
    """

    # Ente Supervisado
    identificacion_ente_supervisado: str = Field(..., max_length=99)

    # Datos del pacto
    tipo_pacto: str = Field(..., max_length=99)
    moneda: str = Field(..., max_length=99)
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
    origen_fondos: str = Field(..., max_length=99)
    medio_pago_oferente: str = Field(..., max_length=99)

    # Cliente Demandante
    identificacion_cliente_demandante: str = Field(..., max_length=20)
    nombre_cliente_demandante: str = Field(..., min_length=1, max_length=100)
    actividad_economica_cliente_demandante: str = Field(..., max_length=99)
    codigo_cuenta_moneda_nacional_demandante: str = Field(..., max_length=20)
    tipo_cuenta_moneda_nacional_cliente_demandante: int
    codigo_cuenta_moneda_extranjera_demandante: str = Field(..., max_length=20)
    tipo_cuenta_moneda_extranjera_cliente_demandante: int
    destino_fondos: str = Field(..., max_length=99)
    medio_pago_demandante: str = Field(..., max_length=99)

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
        """Tipo cuenta moneda nacional must be 8, 9 or 10."""
        if v not in (8, 9, 10):
            raise ValueError('Tipo Cuenta Moneda Nacional Cliente Demandante debe ser 8, 9 o 10')
        return v

    @field_validator('tipo_cuenta_moneda_extranjera_cliente_demandante')
    def validate_tipo_cuenta_extranjera_demandante(cls, v):
        """Tipo cuenta moneda extranjera must be 31 or 32."""
        if v not in (31, 32):
            raise ValueError('Tipo Cuenta Moneda Extranjera Cliente Demandante debe ser 31 o 32')
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
    moneda: str
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
    moneda: Optional[str] = None
    monto_divisa: Optional[Decimal] = None
    tipo_cambio_bs: Optional[Decimal] = None
    contravalor_bs: Optional[Decimal] = None
    nombre_cliente_oferente: Optional[str] = None
    actividad_economica_cliente_oferente: Optional[str] = None
    codigo_cuenta_moneda_nacional_oferente: Optional[str] = None
    tipo_cuenta_moneda_nacional_cliente_oferente: Optional[int] = None
    codigo_cuenta_moneda_extranjera_oferente: Optional[str] = None
    tipo_cuenta_moneda_extranjera_cliente_oferente: Optional[int] = None
    origen_fondos: Optional[str] = None
    medio_pago_oferente: Optional[str] = None
    nombre_cliente_demandante: Optional[str] = None
    actividad_economica_cliente_demandante: Optional[str] = None
    codigo_cuenta_moneda_nacional_demandante: Optional[str] = None
    tipo_cuenta_moneda_nacional_cliente_demandante: Optional[int] = None
    codigo_cuenta_moneda_extranjera_demandante: Optional[str] = None
    tipo_cuenta_moneda_extranjera_cliente_demandante: Optional[int] = None
    destino_fondos: Optional[str] = None
    medio_pago_demandante: Optional[str] = None
