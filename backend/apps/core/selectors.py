from __future__ import annotations

from typing import Any

from apps.core.models import (
    EnteSupervisadoCatalog,
    MecanismoCambiarioCatalog,
    MonedaCatalog,
    ActividadEconomicaCatalog,
    InstrumentoCaptacionCatalog,
    DestinoFondosCatalog,
    MedioPagoCatalog
)

CATALOG_ITEM_FIELDS = ("code", "name", "description", "is_selectable")


def _serialize_catalog_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "code": item["code"],
        "name": item["name"],
        "description": item["description"],
        "is_selectable": item["is_selectable"],
    }


def list_entes_supervisados() -> list[dict[str, Any]]:
    queryset = EnteSupervisadoCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_mecanismos_cambiarios() -> list[dict[str, Any]]:
    queryset = MecanismoCambiarioCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_monedas() -> list[dict[str, Any]]:
    queryset = MonedaCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_actividades_economicas() -> list[dict[str, Any]]:
    queryset = ActividadEconomicaCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_instrumentos_captacion() -> list[dict[str, Any]]:
    queryset = InstrumentoCaptacionCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_destinos_fondos() -> list[dict[str, Any]]:
    queryset = DestinoFondosCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def list_medios_pago() -> list[dict[str, Any]]:
    queryset = MedioPagoCatalog.objects.filter(is_active=True).order_by("sort_order", "code")
    return [_serialize_catalog_item(item) for item in queryset.values(*CATALOG_ITEM_FIELDS)]

def get_intervencion_api01_catalogs() -> dict[str, list[dict[str, Any]]]:
    return {
        "entes_supervisados": list_entes_supervisados(),
        "mecanismos_cambiarios": list_mecanismos_cambiarios(),
        "monedas": list_monedas(),
        "actividades_economicas": list_actividades_economicas(),
        "instrumentos_captacion": list_instrumentos_captacion(),
        "destinos_fondos": list_destinos_fondos(),
        "medios_pago": list_medios_pago(),
    }


def is_valid_ente_supervisado(code: str) -> bool:
    return EnteSupervisadoCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()

def is_valid_mecanismo_cambiario(code: str) -> bool:
    return MecanismoCambiarioCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()

def is_valid_actividad_economica(code: str) -> bool:
    return ActividadEconomicaCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()


def is_valid_moneda(code: str | int) -> bool:
    return MonedaCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()


def is_valid_instrumento_captacion(code: str | int) -> bool:
    return InstrumentoCaptacionCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()


def is_valid_destino_fondos(code: str | int) -> bool:
    return DestinoFondosCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()


def is_valid_medio_pago(code: str | int) -> bool:
    return MedioPagoCatalog.objects.filter(code=str(code).strip(), is_active=True).exists()

def get_moneda(code: str) -> MonedaCatalog | None:
    return MonedaCatalog.objects.filter(code=str(code).strip(), is_active=True).first()
