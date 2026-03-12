from ninja import Schema
from pydantic import field_validator, Field, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from apps.core.utils import parse_rif, validate_rif_range


PositiveDecimalField = condecimal(gt=0, max_digits=20, decimal_places=4)
DecimalField = condecimal(max_digits=20, decimal_places=4)


class MesaDeCambioOperacionInput(Schema):
    """
    Input schema for receiving mesa de cambio operations from internal systems
    """
    codigo_ente_supervisado: str = Field(..., min_length=4, max_length=4)
    codigo_identificacion_operacion: str = Field(..., max_length=20)
    fecha_operacion: datetime
    identificacion_cliente: str = Field(..., max_length=20)
    nombre_cliente: str = Field(..., max_length=100)
    actividad_economica_cliente: str = Field(..., max_length=10)
    moneda: int
    monto_divisa: PositiveDecimalField
    tipo_cambio_bs: PositiveDecimalField
    contravalor_bs: Optional[DecimalField] = None
    codigo_cuenta_moneda_nacional: Optional[str] = Field('0', max_length=20)
    tipo_cuenta_moneda_nacional: Optional[int] = 0
    codigo_cuenta_moneda_extranjera: Optional[str] = Field('0', max_length=20)
    tipo_cuenta_moneda_extranjera: Optional[int] = 0
    destino_fondos: int
    medio_pago: int

    @field_validator('identificacion_cliente')
    def validate_rif(cls, v):
        rif_type, rif_number = parse_rif(v)
        if not rif_type:
            raise ValueError('Formato RIF inválido')
        if not validate_rif_range(rif_type, rif_number):
            raise ValueError('Número de RIF fuera de rango permitido')
        return v.upper()

    @field_validator('moneda')
    def validate_moneda(cls, v):
        if v == 928:
            raise ValueError('Moneda no puede ser Bolívar (928)')
        return v


class MesaDeCambioBatchInput(Schema):
    """Schema for receiving multiple mesa de cambio operations"""
    operaciones: List[MesaDeCambioOperacionInput]
    webhook_url: Optional[str] = None


class MesaDeCambioOperacionOutput(Schema):
    """Output schema for mesa de cambio operation data"""
    id: int
    codigo_identificacion_operacion: str
    fecha_operacion: datetime
    nombre_cliente: str
    identificacion_cliente: str
    monto_divisa: Decimal
    tipo_cambio_bs: Decimal
    contravalor_bs: Decimal
    status: str
    error_code: Optional[int] = None
    error_detail: Optional[str] = None
    created_at: datetime


class MesaDeCambioCorreccionInput(Schema):
    """Schema for correcting rejected mesa de cambio operations"""
    nombre_cliente: Optional[str] = None
    actividad_economica_cliente: Optional[str] = None
    monto_divisa: Optional[Decimal] = None
    tipo_cambio_bs: Optional[Decimal] = None
    codigo_cuenta_moneda_nacional: Optional[str] = None
    tipo_cuenta_moneda_nacional: Optional[int] = None
    codigo_cuenta_moneda_extranjera: Optional[str] = None
    tipo_cuenta_moneda_extranjera: Optional[int] = None
    destino_fondos: Optional[int] = None
    medio_pago: Optional[int] = None
