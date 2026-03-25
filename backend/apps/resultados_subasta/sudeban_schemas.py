from ninja import Schema
from typing import List, Optional

class ResultadoSudebanSchema(Schema):
    """
    Exact schema for SUDEBAN API-03 as per manual
    """
    fechaRecepcionFondos: str # Format: AAAA-MM-DDTHH:MM:SS.sss
    fechaSubasta: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    codigoSubasta: str
    idTipoOperacion: int
    estatusSolicitudCliente: str
    fechaSolicitudCliente: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    idMoneda: int
    montoFinalDivisa: str  # With 4 decimals
    tasaCambioFinalBs: str  # With 4 decimals
    contravalorFinalBs: str  # With 4 decimals
    rifCiCliente: str
    nombreCliente: str
    idActEconomicaCliente: str
    nroCtaBancariaCliente: str  # 20 digits
    idTipoCtaBancariaCliente: int  
    nroCtaBancariaExtCliente: str  # 20 digits
    idTipoCtaBancariaExtCliente: int  
    idDestinoFondos: int
    idMedioPago: int 


class ResultadoSudebanRequestSchema(Schema):
    """
    Complete request schema for SUDEBAN API-03
    """
    idEntidadBancaria: str
    transacciones: List[ResultadoSudebanSchema]
    webhookUrl: Optional[str] = None
