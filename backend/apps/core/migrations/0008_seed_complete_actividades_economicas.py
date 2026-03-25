# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
from pathlib import Path

from django.db import migrations, models


def _load_actividades_from_seed_py_py() -> list[tuple[str, str, str, str, str, str, str]]:
    """Load the actividades list from the provided seed file (.py.py) without executing it."""
    seed_path = Path(__file__).with_name("0008_seed_complete_actividades_economicas.py.py")
    if not seed_path.exists():
        raise RuntimeError(f"Seed file not found: {seed_path}")

    source = seed_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    actividades_node = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "seed_complete_actividades_economicas":
            for stmt in node.body:
                if isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Name) and target.id == "actividades":
                            actividades_node = stmt.value
                            break
                if actividades_node is not None:
                    break
        if actividades_node is not None:
            break

    if actividades_node is None:
        raise RuntimeError("Could not locate 'actividades = [...]' inside seed_complete_actividades_economicas")

    actividades = ast.literal_eval(actividades_node)
    if not isinstance(actividades, list):
        raise RuntimeError("Seed actividades is not a list")

    return actividades


def seed_complete_actividades_economicas(apps, schema_editor):
    ActividadEconomicaCatalog = apps.get_model("core", "ActividadEconomicaCatalog")

    # Reemplaza el catálogo completo para mantener consistencia con el Excel.
    ActividadEconomicaCatalog.objects.all().delete()

    actividades = _load_actividades_from_seed_py_py()

    seen_codes: set[str] = set()
    duplicates: set[str] = set()
    objects = []

    for i, item in enumerate(actividades):
        # item: (full_code, name, section, division, group, class_code, rama_code)
        if not isinstance(item, (tuple, list)) or len(item) != 7:
            raise RuntimeError(f"Invalid actividad row at index {i}: expected 7-tuple, got {item!r}")

        full_code, name, section, division, group, class_code, rama_code = item
        sudeban_code = str(rama_code).strip()
        if not sudeban_code:
            raise RuntimeError(f"Empty rama_code at index {i}: {item!r}")

        if sudeban_code in seen_codes:
            duplicates.add(sudeban_code)
        else:
            seen_codes.add(sudeban_code)

        objects.append(
            ActividadEconomicaCatalog(
                code=sudeban_code,
                name=str(name).strip(),
                description=str(full_code).strip(),
                sort_order=i,
                is_selectable=True,
            )
        )

    if duplicates:
        raise RuntimeError(f"Duplicate rama_code values found in seed: {sorted(duplicates)[:20]}")

    ActividadEconomicaCatalog.objects.bulk_create(objects, batch_size=1000)


def reverse_seed(apps, schema_editor):
    ActividadEconomicaCatalog = apps.get_model("core", "ActividadEconomicaCatalog")
    ActividadEconomicaCatalog.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0007_seed_additional_catalogs"),
    ]

    operations = [
        migrations.AlterField(
            model_name="actividadeconomicacatalog",
            name="code",
            field=models.CharField(max_length=10, unique=True),
        ),
        migrations.RunPython(seed_complete_actividades_economicas, reverse_seed),
    ]
