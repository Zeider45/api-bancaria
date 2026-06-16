"""Catalog updates from the SUDEBAN "API Bancaria" manuals (09-06-2026 update).

- T005 (Instrumento de Captación): reorder the descriptions of codes 8, 9 and 10.
- T002 (Mecanismo Cambiario): add codes 10 and 11 (API-01 Intervención).
- T006 (Destino de los Fondos): add code 0 "No Aplica" (API-01 Intervención).

Only catalog descriptions / entries change; the numeric codes used by the
validation logic are unaffected.
"""

from django.db import migrations


# T005 - Instrumento de Captación: nuevas descripciones para 8/9/10.
INSTRUMENTOS_T005 = {
    '8': 'Cuenta Corriente No Remunerada',
    '9': 'Cuenta Corriente Remunerada',
    '10': 'Depósito de Ahorro',
}

# T005 - descripciones previas (para la reversa de la migración).
INSTRUMENTOS_T005_PREVIO = {
    '8': 'Depósito de Ahorro',
    '9': 'Cuenta Corriente No Remunerada',
    '10': 'Cuenta Corriente Remunerada',
}

# T002 - Mecanismo Cambiario: códigos nuevos.
MECANISMOS_NUEVOS = [
    ('10', 'TOTAL de Fondos Recibidos de BCV para Intervención Cambiaria',
     'Total de fondos recibidos del Banco Central de Venezuela (BCV) para Intervención Cambiaria.', 10, True),
    ('11', 'Otros Fondos que el BCV mantiene en la Institución Bancaria para ser vendidos mediante Intervención',
     'Otros fondos que el BCV mantiene en la Institución Bancaria para ser vendidos mediante Intervención.', 11, True),
]

# T006 - Destino de los Fondos: código 0 "No Aplica".
DESTINOS_NUEVOS = [
    ('0', 'No Aplica', 'No aplica destino de los fondos.', 0, True),
]


def apply_updates(apps, schema_editor):
    InstrumentoCaptacionCatalog = apps.get_model('core', 'InstrumentoCaptacionCatalog')
    MecanismoCambiarioCatalog = apps.get_model('core', 'MecanismoCambiarioCatalog')
    DestinoFondosCatalog = apps.get_model('core', 'DestinoFondosCatalog')

    for code, name in INSTRUMENTOS_T005.items():
        InstrumentoCaptacionCatalog.objects.filter(code=code).update(name=name)

    for code, name, description, sort_order, is_selectable in MECANISMOS_NUEVOS:
        MecanismoCambiarioCatalog.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'sort_order': sort_order,
                'is_selectable': is_selectable,
                'is_active': True,
                'deleted_at': None,
            },
        )

    for code, name, description, sort_order, is_selectable in DESTINOS_NUEVOS:
        DestinoFondosCatalog.objects.update_or_create(
            code=code,
            defaults={
                'name': name,
                'description': description,
                'sort_order': sort_order,
                'is_selectable': is_selectable,
                'is_active': True,
                'deleted_at': None,
            },
        )


def reverse_updates(apps, schema_editor):
    InstrumentoCaptacionCatalog = apps.get_model('core', 'InstrumentoCaptacionCatalog')
    MecanismoCambiarioCatalog = apps.get_model('core', 'MecanismoCambiarioCatalog')
    DestinoFondosCatalog = apps.get_model('core', 'DestinoFondosCatalog')

    for code, name in INSTRUMENTOS_T005_PREVIO.items():
        InstrumentoCaptacionCatalog.objects.filter(code=code).update(name=name)

    MecanismoCambiarioCatalog.objects.filter(code__in=[c[0] for c in MECANISMOS_NUEVOS]).delete()
    DestinoFondosCatalog.objects.filter(code__in=[c[0] for c in DESTINOS_NUEVOS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_sudebanwebhookevent'),
    ]

    operations = [
        migrations.RunPython(apply_updates, reverse_updates),
    ]
