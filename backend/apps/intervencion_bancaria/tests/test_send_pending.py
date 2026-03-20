from __future__ import annotations

from unittest.mock import patch

from django.test import TestCase, override_settings

from apps.intervencion_bancaria import services


class SendPendingIntervencionTests(TestCase):
    @override_settings(
        SUDEBAN_API_URL="https://sudeban.example.test/transmission",
        SUDEBAN_USERNAME="user",
        SUDEBAN_PASSWORD="pass",
        SUDEBAN_ID_ENTIDAD_BANCARIA="0108",
    )
    @patch("apps.core.vpn_client.SudebanAPIClient.send_transaction")
    def test_sends_empty_payload_when_no_pending(self, mock_send_transaction):
        mock_send_transaction.return_value = {
            "success": True,
            "status_code": 200,
            "data": {"ok": True},
        }

        result = services.send_pending_transacciones(webhook_url="https://webhook.example.test")

        self.assertTrue(result["success"])
        self.assertEqual(result["total_pending"], 0)

        mock_send_transaction.assert_called_once()
        endpoint, payload = mock_send_transaction.call_args.args

        self.assertEqual(endpoint, "intervencion-cambiaria")
        self.assertEqual(payload["idEntidadBancaria"], "0108")
        self.assertEqual(payload["transacciones"], [])
        self.assertEqual(payload["webhookUrl"], "https://webhook.example.test")

    @override_settings(
        SUDEBAN_ID_ENTIDAD_BANCARIA=None,
    )
    @patch("apps.core.vpn_client.SudebanAPIClient.send_transaction")
    def test_returns_error_when_no_pending_and_no_ente_code(self, mock_send_transaction):
        result = services.send_pending_transacciones(webhook_url=None)

        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "missing_ente_code")
        mock_send_transaction.assert_not_called()
