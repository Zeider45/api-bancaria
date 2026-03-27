from ninja import Schema
from pydantic import field_validator, Field, model_validator, condecimal
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from apps.core.utils import parse_rif, validate_rif_range
from apps.core import selectors as core_selectors

# Use Decimal directly with pydantic validators if condecimal has issues in newer pydantic
PositiveDecimalField = condecimal(ge=0, max_digits=20, decimal_places=4)
DecimalField = condecimal(ge=0, max_digits=20, decimal_places=4)


class ResultadoSubastaInput(Schema):
    """
    Input schema for receiving subasta results
    Based on SIB-MET-API-03 manual
    """
    codigo_ente_supervisado: Optional[str] = Field(None, min_length=4, max_length=4)
    fecha_recepcion_fondos: datetime
    fecha_subasta: datetime
    codigo_identificacion_subasta: str = Field(..., max_length=50)

    # Resultados
    tipo_operacion: int
    estatus_solicitud_cliente: str = Field(..., max_length=3)
    
    fecha_solicitud_cliente: datetime
    moneda: int
    monto_final_divisa: DecimalField
    tipo_cambio_final_bs: DecimalField
    contravalor_final_bs: Optional[DecimalField] = None

    identificacion_cliente: str = Field(..., max_length=20)
    nombre_cliente: str = Field(..., max_length=100)
    actividad_economica_cliente: str = Field(..., max_length=10)

    codigo_cuenta_moneda_nacional: str = Field(..., min_length=20, max_length=20)
    tipo_cuenta_moneda_nacional: int
    codigo_cuenta_moneda_extranjera: str = Field(..., min_length=20, max_length=20)
    tipo_cuenta_moneda_extranjera: int

    destino_fondos: int
    medio_pago: int

    @field_validator('codigo_ente_supervisado')
    def validate_ente_supervisado(cls, v: str):
        if v is None:
            return v
        if not core_selectors.is_valid_ente_supervisado(v):
            raise ValueError('Código Ente Supervisado inválido (no existe en el catálogo)')
        return str(v).strip()

    @model_validator(mode='after')
    def validate_cross_fields(self):
        """Cross-field validations based on API-03 rules"""
        # Tipo Operacion 8: Adquisicion, 9: Ventas
        if self.tipo_operacion == 8:
            if self.codigo_identificacion_subasta != "0":
                raise ValueError('Si tipo_operacion es 8, codigo_identificacion_subasta debe ser "0"')
            if self.estatus_solicitud_cliente != "SA":
                raise ValueError('Si tipo_operacion es 8, estatus_solicitud_cliente debe ser "SA"')
            if self.fecha_subasta.strftime('%Y-%m-%d') != '1900-01-01':
                raise ValueError('Si tipo_operacion es 8, fecha_subasta debe ser 1900-01-01')
            if self.fecha_solicitud_cliente.strftime('%Y-%m-%d') != '1900-01-01':
                raise ValueError('Si tipo_operacion es 8, fecha_solicitud_cliente debe ser 1900-01-01')
        elif self.tipo_operacion == 9:
            if self.codigo_identificacion_subasta == "0":
                raise ValueError('Si tipo_operacion es 9, codigo_identificacion_subasta no debe ser "0"')
            if self.fecha_solicitud_cliente.date() != self.fecha_subasta.date():
                raise ValueError('Si tipo_operacion es 9, fecha_solicitud_cliente debe ser igual a fecha_subasta')
        else:
            raise ValueError('tipo_operacion debe ser 8 o 9')

        # Relacion con SA / SNA
        if self.estatus_solicitud_cliente == "SA":
            if self.monto_final_divisa <= 0:
                raise ValueError('Si es SA, monto_final_divisa debe ser mayor a 0')
            if self.tipo_cambio_final_bs <= 0:
                raise ValueError('Si es SA, tipo_cambio_final_bs debe ser mayor a 0')
            if self.destino_fondos == 0:
                raise ValueError('Si es SA, destino_fondos no puede ser 0')
            if self.medio_pago != 2:
                raise ValueError('Si es SA, medio_pago debe ser 2 (Transferencia)')
        elif self.estatus_solicitud_cliente == "SNA":
            if self.monto_final_divisa != 0:
                raise ValueError('Si es SNA, monto_final_divisa debe ser 0')
            if self.tipo_cambio_final_bs != 0:
                raise ValueError('Si es SNA, tipo_cambio_final_bs debe ser 0')
            if self.destino_fondos != 0:
                raise ValueError('Si es SNA, destino_fondos debe ser 0')
            if self.medio_pago != 0:
                raise ValueError('Si es SNA, medio_pago debe ser 0')
        else:
            raise ValueError('estatus_solicitud_cliente inválido (debe ser SA o SNA)')

        return self

    @field_validator('identificacion_cliente')
    def validate_rif(cls, v):
        rif_type, rif_number = parse_rif(v)
        if not rif_type:
            raise ValueError('Formato RIF inválido.')
        if not validate_rif_range(rif_type, rif_number):
            raise ValueError('Número de RIF fuera de rango permitido')
        return v.upper()

    @field_validator('moneda')
    def validate_moneda(cls, v):
        if v == 928:
            raise ValueError('Moneda no puede ser Bolívar (928)')
        if not core_selectors.is_valid_moneda(v):
            raise ValueError('Moneda inválida (no existe en el catálogo)')
        return v

    @field_validator('actividad_economica_cliente')
    def validate_actividad_economica(cls, v: str):
        if not core_selectors.is_valid_actividad_economica(v):
            raise ValueError('Actividad Económica inválida (no existe en el catálogo)')
        return str(v).strip()

    @field_validator('tipo_cuenta_moneda_nacional')
    def validate_tipo_cuenta_nacional(cls, v):
        if v not in [8, 9, 10]:
            raise ValueError('Tipo cuenta nacional debe ser 8, 9 o 10')
        if not core_selectors.is_valid_instrumento_captacion(v):
            raise ValueError('Tipo cuenta nacional inválida (no existe en el catálogo)')
        return v

    @field_validator('tipo_cuenta_moneda_extranjera')
    def validate_tipo_cuenta_extranjera(cls, v):
        if v not in [31, 32]:
            raise ValueError('Tipo cuenta extranjera debe ser 31 o 32')
        if not core_selectors.is_valid_instrumento_captacion(v):
            raise ValueError('Tipo cuenta extranjera inválida (no existe en el catálogo)')
        return v

    @field_validator('destino_fondos')
    def validate_destino_fondos(cls, v: int):
        # En API-03: SA requiere destino != 0; SNA requiere destino=0 (validación cruzada).
        # Si viene distinto de 0, debe existir en el catálogo.
        if v is None:
            raise ValueError('Destino de Fondos es requerido')
        if int(v) != 0 and not core_selectors.is_valid_destino_fondos(v):
            raise ValueError('Destino de Fondos inválido (no existe en el catálogo)')
        return int(v)

    @field_validator('medio_pago')
    def validate_medio_pago(cls, v: int):
        # En API-03: SA requiere medio_pago=2; SNA requiere medio_pago=0 (validación cruzada).
        # Si viene distinto de 0, debe existir en el catálogo.
        if v is None:
            raise ValueError('Medio de Pago es requerido')
        if int(v) != 0 and not core_selectors.is_valid_medio_pago(v):
            raise ValueError('Medio de Pago inválido (no existe en el catálogo)')
        return int(v)


class ResultadoBatchInput(Schema):
    """Schema for receiving multiple resultados"""
    transacciones: List[ResultadoSubastaInput]
    webhook_url: Optional[str] = None


class ResultadoSubastaOutput(Schema):
    """Output schema for resultado data"""
    id: int
    codigo_identificacion_subasta: str
    fecha_subasta: datetime
    estatus_solicitud_cliente: str
    nombre_cliente: str
    identificacion_cliente: str
    monto_final_divisa: Decimal
    tipo_cambio_final_bs: Decimal
    contravalor_final_bs: Decimal
    status: str
    error_code: Optional[int] = None
    error_detail: Optional[str] = None
    created_at: datetime
