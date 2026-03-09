from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from apps.subasta_privada.services import create_solicitud, validate_solicitud_for_sudeban, prepare_for_sudeban
from apps.subasta_privada.serializers import SubastaSolicitudInput
from decimal import Decimal


class Command(BaseCommand):
    help = 'Test subasta privada functionality'
    
    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Subasta Privada (API-02)...")
        
        # Create test data
        now = timezone.now()
        
        test_data = SubastaSolicitudInput(
            codigo_ente_supervisado="0108",
            fecha_subasta=now,
            codigo_identificacion_subasta=f"TEST-{now.strftime('%Y%m%d-%H%M%S')}",
            fecha_solicitud_cliente=now,
            moneda=840,
            identificacion_cliente="J123456789",
            nombre_cliente="EMPRESA DE PRUEBA C.A",
            actividad_economica_cliente="5510",
            monto_divisa=Decimal("10000.0000"),
            tipo_cambio_bs=Decimal("380.1234"),
            codigo_cuenta_moneda_nacional="01081000216640034521",
            tipo_cuenta_moneda_nacional=8,
            codigo_cuenta_moneda_extranjera="01082121032647221067",
            tipo_cuenta_moneda_extranjera=31,
            destino_fondos=3,
            medio_pago=2
        )
        
        self.stdout.write("✅ Test data created")
        
        # Test validation
        try:
            solicitud = create_solicitud(test_data)
            self.stdout.write(self.style.SUCCESS(f"✅ Created solicitud: {solicitud.id}"))
            
            # Test SUDEBAN validation
            is_valid, errors = validate_solicitud_for_sudeban(solicitud)
            if is_valid:
                self.stdout.write(self.style.SUCCESS("✅ Validation passed"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Validation failed: {errors}"))
            
            # Test SUDEBAN format
            sudeban_data = prepare_for_sudeban(solicitud)
            self.stdout.write("✅ Prepared for SUDEBAN:")
            self.stdout.write(str(sudeban_data.dict()))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))