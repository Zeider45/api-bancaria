from django.core.management.base import BaseCommand
from django.conf import settings
from apps.core.vpn_client import SudebanAPIClient
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Test VPN connection to SUDEBAN'
    
    def add_arguments(self, parser):
        parser.add_argument('--test-data', action='store_true', help='Send test transaction')
    
    def handle(self, *args, **options):
        self.stdout.write("Testing VPN connection to SUDEBAN...")
        
        client = SudebanAPIClient(
            base_url=settings.SUDEBAN_API_URL,
            username=settings.SUDEBAN_USERNAME,
            password=settings.SUDEBAN_PASSWORD,
            verify_ssl=True
        )
        
        # Test basic connectivity
        if client.test_connection():
            self.stdout.write(self.style.SUCCESS("✓ VPN Connection successful"))
        else:
            self.stdout.write(self.style.ERROR("✗ VPN Connection failed"))
            return
        
        if options['test_data']:
            self.stdout.write("\nSending test transaction...")
            
            test_data = {
                "idEntidadBancaria": "0134",  # Example
                "transacciones": [{
                    "idTipIntervencion": "1",
                    "fechalIntervencion": "2026-01-20T14:00:00.000",
                    "codigolIntervencion": "TEST001",
                    "fechaOperacionCliente": "2026-01-21T11:30:35.000",
                    "idMoneda": 840,
                    "rifCiCliente": "V24146389",
                    "nombreCliente": "Test Cliente",
                    "idActEconomicaCliente": "4620",
                    "montoDivisa": "1000.0000",
                    "tasaCambioBs": "360.2534",
                    "contravalorBs": "360253.4000",
                    "nroCtaBancariaCliente": "01341000146203340021",
                    "idTipoCtaBancariaCliente": 8,
                    "nroCtaBancariaExtCliente": "01342103276467202121",
                    "idTipoCtaBancariaExtCliente": 31,
                    "idDestinoFondos": 3,
                    "idMedioPago": 2
                }]
            }
            
            result = client.send_transaction('intervencion-cambiaria', test_data)
            
            if result['success']:
                self.stdout.write(self.style.SUCCESS("✓ Test transaction successful"))
                self.stdout.write(f"Response: {result.get('data')}")
            else:
                self.stdout.write(self.style.ERROR(f"✗ Test transaction failed: {result.get('detail')}"))