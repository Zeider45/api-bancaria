import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SudebanIntervencionClient:
    """
    Specialized client for API-01 Intervención Cambiaria
    """
    
    def __init__(self):
        self.base_url = settings.SUDEBAN_API_URL
        self.endpoint = "intervencion-cambiaria"
        self.username = settings.SUDEBAN_USERNAME
        self.password = settings.SUDEBAN_PASSWORD
        self.timeout = 30
    
    def send_transacciones(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send transactions to SUDEBAN
        """
        url = f"{self.base_url}/{self.endpoint}"
        
        try:
            response = requests.post(
                url,
                json=data,
                auth=(self.username, self.password),
                timeout=self.timeout,
                verify=not settings.DEBUG
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': response.json()
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending to SUDEBAN: {e}")
            return {
                'success': False,
                'error': str(e)
            }