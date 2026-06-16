from ninja import Schema
from pydantic import field_validator, Field, model_validator, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from apps.core import selectors
from apps.core.utils import (
    is_valid_identificacion_cliente,
    validate_nombre_cliente as validate_nombre_cliente_util,
)


DecimalField = condecimal(max_digits=20, decimal_places=4)


class IntervencionTransaccionInput(Schema):
    """
    Input schema for receiving transactions from internal systems
    """
    codigo_operacion: str = Field(..., max_length=40)  # API-01: identificación única de la operación
    codigo_ente_supervisado: Optional[str] = Field(None, min_length=4, max_length=4)
    tipo_intervencion: str
    fecha_intervencion: datetime
    codigo_identificacion_intervencion: str = Field(..., max_length=10)
    fecha_operacion_cliente: datetime
    moneda: int
    identificacion_cliente: str = Field(..., max_length=20)
    nombre_cliente: str = Field(..., max_length=100)
    actividad_economica_cliente: str = Field(..., max_length=10)
    monto_divisa: DecimalField
    tipo_cambio_bs: DecimalField
    contravalor_bs: Optional[DecimalField] = None
    codigo_cuenta_moneda_nacional: Optional[str] = Field('0', max_length=20)
    tipo_cuenta_moneda_nacional: Optional[int] = 0
    codigo_cuenta_moneda_extranjera: Optional[str] = Field('0', max_length=20)
    tipo_cuenta_moneda_extranjera: Optional[int] = 0
    destino_fondos: int
    medio_pago: int

    @field_validator('codigo_ente_supervisado')
    def validate_codigo_ente_supervisado(cls, v):
        if v is None:
            return v
        if not selectors.is_valid_ente_supervisado(v):
            raise ValueError('Código de ente supervisado inválido (T001)')
        return v

    @field_validator('tipo_intervencion')
    def validate_tipo_intervencion(cls, v):
        normalized = str(v).strip()
        if not selectors.is_valid_mecanismo_cambiario(normalized):
            raise ValueError('Tipo de intervención inválido (T002)')
        return normalized

    @model_validator(mode='after')
    def validate_fechas(self):
        """Validate fecha_operacion_cliente <= fecha_intervencion."""
        if self.fecha_operacion_cliente > self.fecha_intervencion:
            raise ValueError('Fecha operación no puede ser mayor a fecha intervención')
        return self
    
    @field_validator('codigo_operacion', 'codigo_identificacion_intervencion')
    def validate_texto_sin_simbolos(cls, v):
        """Código de la Operación / Identificación: distinto de 0/vacío/Null y
        sin caracteres ni símbolos no permitidos (API-01)."""
        return validate_nombre_cliente_util(v)

    @field_validator('identificacion_cliente')
    def validate_rif(cls, v):
        """Validate client identification (RIF SENIAT or identity document)."""
        if not is_valid_identificacion_cliente(v):
            raise ValueError(
                'Identificación de cliente inválida (verifique el prefijo, el RIF '
                'emitido por SENIAT o el documento de identificación)'
            )
        return v.strip().upper()

    @field_validator('nombre_cliente')
    def validate_nombre_cliente(cls, v):
        return validate_nombre_cliente_util(v)
    
    @field_validator('moneda')
    def validate_moneda(cls, v):
        """Validate currency code"""
        moneda = selectors.get_moneda(str(v))
        if not moneda:
            raise ValueError('Código de moneda inválido (T003)')
        if not moneda.is_selectable:
            raise ValueError('Moneda no puede ser Bolívar (928)')
        return v

    @field_validator('actividad_economica_cliente')
    def validate_actividad_economica(cls, v):
        normalized = str(v).strip()
        if not selectors.is_valid_actividad_economica(normalized):
            raise ValueError('Actividad económica inválida (T004)')
        return normalized


class IntervencionBatchInput(Schema):
    """Schema for receiving multiple transactions"""
    transacciones: List[IntervencionTransaccionInput]
    webhook_url: Optional[str] = None


class IntervencionTransaccionOutput(Schema):
    """Output schema for transaction data"""
    id: int
    codigo_identificacion_intervencion: str
    fecha_operacion_cliente: datetime
    nombre_cliente: str
    monto_divisa: Decimal
    tipo_cambio_bs: Decimal
    contravalor_bs: Decimal
    status: str
    error_code: Optional[int] = None
    error_detail: Optional[str] = None
    created_at: datetime


class IntervencionCorreccionInput(Schema):
    """Schema for correcting rejected transactions"""
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