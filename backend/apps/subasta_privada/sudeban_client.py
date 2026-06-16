import requests
import logging
from typing import Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class SudebanSubastaClient:
    """
    Specialized client for API-02 Subasta Privada
    """
    
    def __init__(self):
        self.base_url = settings.SUDEBAN_API_URL
        self.endpoint = "libro-ordenes-subasta"
        self.username = settings.SUDEBAN_USERNAME
        self.password = settings.SUDEBAN_PASSWORD
        self.timeout = 30
    
    def send_solicitudes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send subasta requests to SUDEBAN
        """
        url = f"{self.base_url}/{self.endpoint}"
        
        try:
            logger.info(f"Sending subasta batch to {url}")
            response = requests.post(
                url,
                json=data,
                auth=(self.username, self.password),
                timeout=self.timeout,
                verify=not settings.DEBUG
            )
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"SUDEBAN response: {result}")
            
            return {
                'success': True,
                'status_code': response.status_code,
                'data': result
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout sending to SUDEBAN")
            return {
                'success': False,
                'error': 'timeout',
                'detail': 'Connection timeout'
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            return {
                'success': False,
                'error': 'connection_error',
                'detail': str(e)
            }
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            error_detail = str(e)
            try:
                error_detail = response.json()
            except:
                pass
            
            return {
                'success': False,
                'error': 'http_error',
                'status_code': response.status_code if 'response' in locals() else None,
                'detail': error_detail
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                'success': False,
                'error': 'unexpected_error',
                'detail': str(e)
            }