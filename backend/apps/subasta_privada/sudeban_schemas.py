from ninja import Schema
from typing import List, Optional


class SudebanSolicitudSchema(Schema):
    """
    Exact schema for SUDEBAN API-02 as per manual (page 27)
    """
    fechaSubasta: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    codigoSubasta: str
    fechaSolicitudCliente: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    idMoneda: int
    rifCiCliente: str
    nombreCliente: str
    idActEconomicaCliente: str
    montoDivisa: str  # With 4 decimals
    tasaCambioBs: str  # With 4 decimals
    contravalorBs: str  # With 4 decimals
    nroCtaBancariaCliente: str  # 20 digits
    idTipoCtaBancariaCliente: int  # 8, 9, 10
    nroCtaBancariaExtCliente: str  # 20 digits
    idTipoCtaBancariaExtCliente: int  # 31, 32
    idDestinoFondos: int
    idMedioPago: int  # Must be 2 for subasta


class SudebanRequestSchema(Schema):
    """
    Complete request schema for SUDEBAN API-02
    """
    idEntidadBancaria: str
    transacciones: List[SudebanSolicitudSchema]
    webhookUrl: Optional[str] = None