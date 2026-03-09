from ninja import Schema
from typing import List, Optional


class SudebanMesaDeCambioTransaccionSchema(Schema):
    """
    Exact schema for SUDEBAN Mesa de Cambio transactions as per operational manual.
    Field names follow camelCase convention required by SUDEBAN.
    """
    tipoPacto: str
    moneda: str
    fechaPacto: str                      # Format: AAAA-MM-DDTHH:MM:SS.sss
    montoDivisa: str                     # With 4 decimal places
    tipoCambioBs: str                    # With 4 decimal places
    contraValorBs: str                   # With 4 decimal places

    # Oferente
    identificacionClienteOferente: str
    nombreClienteOferente: str
    actEconomicaClienteOferente: str
    codCtaMnOferente: str                # 20-digit national currency account
    tipCtaMnClienteOferente: int         # 8, 9 or 10
    codCtaMeOferente: str                # 20-digit foreign currency account
    tipCtaMeClienteOferente: int         # 31 or 32
    origenFondos: str
    medioPagoOferente: str

    # Demandante
    identificacionClienteDemandante: str
    nombreClienteDemandante: str
    actEconomicaClienteDemandante: str
    codCtaMnDemandante: str              # 20-digit national currency account
    tipCtaMnClienteDemandante: int       # 8, 9 or 10
    codCtaMeDemandante: str              # 20-digit foreign currency account
    tipCtaMeClienteDemandante: int       # 31 or 32
    destinoFondos: str
    medioPagoDemandante: str


class SudebanMesaDeCambioRequestSchema(Schema):
    """
    Complete request payload schema for SUDEBAN Mesa de Cambio endpoint.
    """
    idEntidadBancaria: str
    transacciones: List[SudebanMesaDeCambioTransaccionSchema]
    webhookUrl: Optional[str] = None
