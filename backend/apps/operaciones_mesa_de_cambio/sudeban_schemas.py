from ninja import Schema
from typing import List, Optional


class SudebanMesaDeCambioTransaccionSchema(Schema):
    """Exact schema for SUDEBAN API-04 (Mesa de Cambio) as per manual.

    Field names are intentionally kept exactly as required by SUDEBAN.
    """

    idTipoPacto: str
    idMoneda: int
    fechaPacto: str  # Format: AAAA-MM-DDTHH:MM:SS.sss
    montoDivisa: str  # With 4 decimals
    tasaCambioBs: str  # With 4 decimals
    contravalorBs: str  # With 4 decimals

    # Origen (Cliente oferente)
    rifCiOrigen: str
    nombreClienteOrigen: str
    idActEconomicaOrigen: str
    nroCtaBancariaOrigen: str
    idTipoCtaBancariaOrigen: int
    nroCtaBancariaExtOrigen: str
    idTipoCtaBancariaExtOrigen: int
    idOrigenFondos: int
    idMedioPagoOrigen: int

    # Destino (Cliente demandante)
    rifCiDestino: str
    nombreClienteDestino: str
    idActEconomicaDestino: str
    nroCtaBancariaDestino: str
    idTipoCtaBancariaDestino: int
    nroCtaBancariaExtDestino: str
    idTipoCtaBancariaExtDestino: int
    idDestinoFondos: int
    idMedioPagoDestino: int


class SudebanMesaDeCambioRequestSchema(Schema):
    """
    Complete request payload schema for SUDEBAN Mesa de Cambio endpoint.
    """
    idEntidadBancaria: str
    transacciones: List[SudebanMesaDeCambioTransaccionSchema]
    webhookUrl: Optional[str] = None
