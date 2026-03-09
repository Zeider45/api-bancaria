import logging
from typing import Any, Dict, Optional

import requests


logger = logging.getLogger(__name__)


class SudebanAPIClient:
	"""Basic HTTP client for SUDEBAN endpoints over the configured VPN."""

	def __init__(
		self,
		base_url: str,
		username: Optional[str] = None,
		password: Optional[str] = None,
		verify_ssl: bool = True,
		timeout: int = 30,
	):
		self.base_url = base_url.rstrip('/')
		self.username = username
		self.password = password
		self.verify_ssl = verify_ssl
		self.timeout = timeout

	def _request(self, method: str, url: str, **kwargs) -> requests.Response:
		auth = None
		if self.username and self.password:
			auth = (self.username, self.password)

		return requests.request(
			method=method,
			url=url,
			auth=auth,
			timeout=self.timeout,
			verify=self.verify_ssl,
			**kwargs,
		)

	def test_connection(self) -> bool:
		try:
			response = self._request('GET', self.base_url)
			return response.ok
		except requests.RequestException as exc:
			logger.error('Error testing SUDEBAN connection: %s', exc)
			return False

	def send_transaction(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
		url = f"{self.base_url}/{endpoint.lstrip('/')}"

		try:
			response = self._request('POST', url, json=payload)
			response.raise_for_status()

			try:
				data = response.json()
			except ValueError:
				data = response.text

			return {
				'success': True,
				'status_code': response.status_code,
				'data': data,
			}
		except requests.exceptions.Timeout:
			logger.error('Timeout sending payload to SUDEBAN: %s', endpoint)
			return {
				'success': False,
				'error': 'timeout',
				'detail': 'Connection timeout',
			}
		except requests.exceptions.ConnectionError as exc:
			logger.error('Connection error sending to SUDEBAN: %s', exc)
			return {
				'success': False,
				'error': 'connection_error',
				'detail': str(exc),
			}
		except requests.exceptions.HTTPError as exc:
			logger.error('HTTP error sending to SUDEBAN: %s', exc)
			detail: Any
			try:
				detail = exc.response.json() if exc.response is not None else str(exc)
			except ValueError:
				detail = exc.response.text if exc.response is not None else str(exc)

			return {
				'success': False,
				'error': 'http_error',
				'status_code': exc.response.status_code if exc.response is not None else None,
				'detail': detail,
			}
		except requests.RequestException as exc:
			logger.error('Unexpected request error sending to SUDEBAN: %s', exc)
			return {
				'success': False,
				'error': 'request_error',
				'detail': str(exc),
			}
