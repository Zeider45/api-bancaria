import requests
import logging
from typing import Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class SudebanMesaDeCambioClient:
    """
    Specialized HTTP client for the SUDEBAN Mesa de Cambio endpoint.
    """

    def __init__(self):
        self.base_url = settings.SUDEBAN_API_URL
        self.endpoint = "mesa-cambio"
        self.username = settings.SUDEBAN_USERNAME
        self.password = settings.SUDEBAN_PASSWORD
        self.timeout = 30

    def send_transacciones(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a batch of mesa de cambio transactions to SUDEBAN.
        """
        url = f"{self.base_url}/{self.endpoint}"

        try:
            response = requests.post(
                url,
                json=data,
                auth=(self.username, self.password),
                timeout=self.timeout,
                verify=not settings.DEBUG,
            )

            response.raise_for_status()

            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json(),
            }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending mesa de cambio transactions to SUDEBAN: {e}")
            return {
                'success': False,
                'error': str(e),
            }
