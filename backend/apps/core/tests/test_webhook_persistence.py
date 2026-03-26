from django.test import TestCase

from apps.core.models import SudebanWebhookEvent


class SudebanWebhookPersistenceTests(TestCase):
    def test_webhook_valid_json_is_persisted(self):
        payload = {"status": "rejected", "codigoError": 8388609}
        resp = self.client.post(
            "/api/internal/v1/webhooks/api04/",
            data=payload,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(SudebanWebhookEvent.objects.count(), 1)
        event = SudebanWebhookEvent.objects.first()
        assert event is not None

        self.assertEqual(event.api, "API-04")
        self.assertTrue(event.parse_success)
        self.assertEqual(event.payload, payload)
        self.assertEqual(event.error_code, 8388609)
        self.assertTrue(event.decoded_errors)

    def test_webhook_invalid_json_is_still_persisted(self):
        resp = self.client.post(
            "/api/internal/v1/webhooks/api03/",
            data="{invalid-json",
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, 400)

        self.assertEqual(SudebanWebhookEvent.objects.count(), 1)
        event = SudebanWebhookEvent.objects.first()
        assert event is not None

        self.assertEqual(event.api, "API-03")
        self.assertFalse(event.parse_success)
        self.assertIsNone(event.payload)
        self.assertIn("invalid-json", event.raw_body)
