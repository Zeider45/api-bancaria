from ninja import Schema
from pydantic import field_validator, Field, model_validator, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from apps.core.utils import (
    is_valid_identificacion_cliente,
    validate_nombre_cliente as validate_nombre_cliente_util,
)


PositiveDecimalField = condecimal(gt=0, max_digits=20, decimal_places=4)
DecimalField = condecimal(max_digits=20, decimal_places=4)


class SubastaSolicitudInput(Schema):
    """
    Input schema for receiving subasta requests from internal systems
    Based on SIB-MET-API-02 manual
    """
    # DATOS SUBASTA PRIVADA
    codigo_ente_supervisado: Optional[str] = Field(None, min_length=4, max_length=4)
    fecha_subasta: datetime
    codigo_identificacion_subasta: str = Field(..., max_length=50)
    
    # DATOS DE LA SOLICITUD
    fecha_solicitud_cliente: datetime
    moneda: int
    identificacion_cliente: str = Field(..., max_length=20)
    nombre_cliente: str = Field(..., max_length=100)
    actividad_economica_cliente: str = Field(..., max_length=10)
    monto_divisa: PositiveDecimalField
    tipo_cambio_bs: PositiveDecimalField
    contravalor_bs: Optional[DecimalField] = None
    
    # Cuentas - Always required for subasta
    codigo_cuenta_moneda_nacional: str = Field(..., min_length=20, max_length=20)
    tipo_cuenta_moneda_nacional: int
    codigo_cuenta_moneda_extranjera: str = Field(..., max_length=20)  # API-02: longitud menor o igual a 20
    tipo_cuenta_moneda_extranjera: int

    destino_fondos: int = Field(..., ge=1)  # Must be distinct from 0
    medio_pago: int = Field(..., ge=1)  # Must be distinct from 0
    
    @model_validator(mode='after')
    def validate_fechas(self):
        """Validate that fecha_solicitud_cliente equals fecha_subasta"""
        if self.fecha_solicitud_cliente.date() > self.fecha_subasta.date():
            raise ValueError('fecha_solicitud_cliente debe ser menor o igual a fecha_subasta')
        return self

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
        """Validate currency code - cannot be Bolivar (928)"""
        if v == 928:
            raise ValueError('Moneda no puede ser Bolívar (928)')
        return v
    
    @field_validator('tipo_cuenta_moneda_nacional')
    def validate_tipo_cuenta_nacional(cls, v):
        """Validate national account type"""
        if v not in [8, 9, 10]:
            raise ValueError('Tipo cuenta nacional debe ser 8, 9 o 10')
        return v
    
    @field_validator('tipo_cuenta_moneda_extranjera')
    def validate_tipo_cuenta_extranjera(cls, v):
        """Validate foreign account type"""
        if v not in [31, 32]:
            raise ValueError('Tipo cuenta extranjera debe ser 31 o 32')
        return v
    
    @field_validator('medio_pago')
    def validate_medio_pago(cls, v):
        """Validate payment method - must be 2 for subasta"""
        if v != 2:
            raise ValueError('Para subasta privada, medio_pago debe ser 2 (Transferencia a Cuenta Cliente)')
        return v


class SubastaBatchInput(Schema):
    """Schema for receiving multiple subasta requests"""
    transacciones: List[SubastaSolicitudInput]
    webhook_url: Optional[str] = None


class SubastaSolicitudOutput(Schema):
    """Output schema for subasta request data"""
    id: int
    codigo_identificacion_subasta: str
    fecha_subasta: datetime
    fecha_solicitud_cliente: datetime
    nombre_cliente: str
    identificacion_cliente: str
    monto_divisa: Decimal
    tipo_cambio_bs: Decimal
    contravalor_bs: Decimal
    status: str
    error_code: Optional[int] = None
    error_detail: Optional[str] = None
    created_at: datetime


class SubastaCorreccionInput(Schema):
    """Schema for correcting rejected subasta requests"""
    nombre_cliente: Optional[str] = Field(None, max_length=100)
    actividad_economica_cliente: Optional[str] = Field(None, max_length=10)
    monto_divisa: Optional[PositiveDecimalField] = None
    tipo_cambio_bs: Optional[PositiveDecimalField] = None
    codigo_cuenta_moneda_nacional: Optional[str] = Field(None, min_length=20, max_length=20)
    tipo_cuenta_moneda_nacional: Optional[int] = None
    codigo_cuenta_moneda_extranjera: Optional[str] = Field(None, max_length=20)  # API-02: longitud menor o igual a 20
    tipo_cuenta_moneda_extranjera: Optional[int] = None
    destino_fondos: Optional[int] = Field(None, ge=1)
    medio_pago: Optional[int] = Field(None, ge=1)

    @field_validator('nombre_cliente')
    def validate_nombre_cliente(cls, v):
        if v is None:
            return v
        return validate_nombre_cliente_util(v)

    @field_validator('tipo_cuenta_moneda_nacional')
    def validate_tipo_cuenta_nacional(cls, v):
        if v is not None and v not in [8, 9, 10]:
            raise ValueError('Tipo cuenta nacional debe ser 8, 9 o 10')
        return v
    
    @field_validator('tipo_cuenta_moneda_extranjera')
    def validate_tipo_cuenta_extranjera(cls, v):
        if v is not None and v not in [31, 32]:
            raise ValueError('Tipo cuenta extranjera debe ser 31 o 32')
        return v
    
    @field_validator('medio_pago')
    def validate_medio_pago(cls, v):
        if v is not None and v != 2:
            raise ValueError('Para subasta privada, medio_pago debe ser 2')
        return v