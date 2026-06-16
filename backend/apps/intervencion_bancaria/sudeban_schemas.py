from ninja import Schema
from datetime import datetime
from decimal import Decimal
from typing import List, Optional


class SudebanTransaccionSchema(Schema):
    """
    Exact schema for SUDEBAN API-01 as per manual
    """
    codigoOperacion: str
    idTipIntervencion: str
    fechalIntervencion: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    codigolIntervencion: str
    fechaOperacionCliente: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    idMoneda: int
    rifCiCliente: str
    nombreCliente: str
    idActEconomicaCliente: str
    montoDivisa: str  # With 4 decimals
    tasaCambioBs: str  # With 4 decimals
    contravalorBs: str  # With 4 decimals
    nroCtaBancariaCliente: str
    idTipoCtaBancariaCliente: int
    nroCtaBancariaExtCliente: str
    idTipoCtaBancariaExtCliente: int
    idDestinoFondos: int
    idMedioPago: int


class SudebanRequestSchema(Schema):
    """
    Complete request schema for SUDEBAN
    """
    idEntidadBancaria: str
    transacciones: List[SudebanTransaccionSchema]
    webhookUrl: Optional[str] = None