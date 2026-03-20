from django.db import migrations


ENTES_SUPERVISADOS = [
    ('0102', 'Banco de Venezuela, S.A Banco Universal', '', 1, True),
    ('0104', 'Venezolano de Crédito, S.A Banco Universal', '', 2, True),
    ('0105', 'Mercantil, C.A Banco Universal', '', 3, True),
    ('0108', 'Banco Provincial, S.A Banco Universal', '', 4, True),
    ('0114', 'Banco del Caribe, C.A Banco Universal Bancaribe', '', 5, True),
    ('0115', 'Banco Exterior, C.A Banco Universal', '', 6, True),
    ('0128', 'Banco Caroní, C.A Banco Universal', '', 7, True),
    ('0134', 'Banesco Banco Universal, C.A', '', 8, True),
    ('0137', 'Banco Sofitasa, Banco Universal, C.A', '', 9, True),
    ('0138', 'Banco Plaza, C.A Banco Universal', '', 10, True),
    ('0146', 'Banco de la Gente Emprendedora Bangente, C.A', '', 11, True),
    ('0151', 'BFC Banco Fondo Común, C.A Banco Universal', '', 12, True),
    ('0156', '100% Banco, Banco Universal, C.A', '', 13, True),
    ('0157', 'Del Sur Banco Universal, C.A', '', 14, True),
    ('0163', 'Banco del Tesoro, C.A Banco Universal', '', 15, True),
    ('0166', 'Banco Agrícola de Venezuela, C.A Banco Universal', '', 16, True),
    ('0168', 'Bancrecer, S.A Banco Microfinanciero', '', 17, True),
    ('0169', 'R4 Banco Microfinanciero, C.A', '', 18, True),
    ('0171', 'Banco Activo, C.A Banco Universal', '', 19, True),
    ('0172', 'Bancamiga Banco Microfinanciero, C.A', '', 20, True),
    ('0173', 'Banco Internacional de Desarrollo, C.A', '', 21, True),
    ('0174', 'Banplus Banco Universal, C.A', '', 22, True),
    ('0175', 'Banco Digital de los Trabajadores Banco Universal, C.A', '', 23, True),
    ('0177', 'Banco de la Fuerza Armada Nacional Bolivariana Banco Universal, C.A (Banfanb)', '', 24, True),
    ('0178', 'N58 Banco Digital, Banco Microfinanciero, S.A', '', 25, True),
    ('0191', 'Banco Nacional de Crédito, C.A Banco Universal', '', 26, True),
    ('0601', 'Instituto Municipal de Crédito Popular I.M.C.P', '', 27, True),
    ('3621', 'Banco de Comercio Exterior, C.A Bancoex', '', 28, True),
]

MECANISMOS_CAMBIARIOS = [
    ('1', 'Venta por Intervención BCV', 'Operaciones de Venta a clientes con recursos provenientes de la intervención directa del Banco Central de Venezuela (BCV).', 1, True),
    ('2', 'Compra a operadores Cambiarios', 'Operaciones de Compra a operadores cambiarios para atender exceso de demanda final de la Institución.', 2, True),
    ('3', 'Venta por operaciones Interbancarias', 'Operaciones de Venta a clientes con recursos provenientes de operaciones interbancarias.', 3, True),
    ('4', 'Venta a operadores cambiarios', 'Venta a operadores cambiarios con recursos provenientes de la intervención directa del Banco Central de Venezuela (BCV).', 4, True),
    ('5', 'Compra de divisas al BCV', 'Operaciones de Compra de divisas al Banco Central de Venezuela (BCV), para ser colocadas a través del mecanismo de intervención cambiaria.', 5, True),
    ('6', 'Compra al BCV por convocatoria privada', 'Operación de Compra de Divisas al BCV mediante una convocatoria privada.', 6, True),
    ('7', 'Venta por Convocatoria Privada con BCV', 'Operaciones de Venta a clientes con recursos provenientes de la Convocatoria Privada con el BCV.', 7, True),
]

MONEDAS = [
    ('170', 'COP', 'Pesos Colombianos', 1, True),
    ('643', 'RUB', 'Rublo', 2, True),
    ('840', 'USD', 'Dólar Americano', 3, True),
    ('928', 'VES', 'Bolívar', 4, False),
    ('978', 'EUR', 'Euros', 5, True),
    ('979', 'CNY', 'Yuan Chino', 6, True),
    ('980', 'TRY', 'Lira Turca', 7, True),
]


def seed_catalogs(apps, schema_editor):
    EnteSupervisadoCatalog = apps.get_model('core', 'EnteSupervisadoCatalog')
    MecanismoCambiarioCatalog = apps.get_model('core', 'MecanismoCambiarioCatalog')
    MonedaCatalog = apps.get_model('core', 'MonedaCatalog')

    for code, name, description, sort_order, is_selectable in ENTES_SUPERVISADOS:
        EnteSupervisadoCatalog.objects.update_or_create(
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

    for code, name, description, sort_order, is_selectable in MECANISMOS_CAMBIARIOS:
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

    for code, name, description, sort_order, is_selectable in MONEDAS:
        MonedaCatalog.objects.update_or_create(
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


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_catalogs, migrations.RunPython.noop),
    ]
