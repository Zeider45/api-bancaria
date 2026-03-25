from django.test import SimpleTestCase

from apps.core.utils import decode_sudeban_error


class DecodeSudebanErrorTests(SimpleTestCase):
    def test_single_bit(self):
        messages = decode_sudeban_error(1)
        self.assertTrue(messages)
        self.assertIn("Moneda", messages[0])

    def test_multiple_bits(self):
        messages = decode_sudeban_error(1 | 4)
        joined = " | ".join(messages)
        self.assertIn("Moneda", joined)
        self.assertIn("Actividad Económica", joined)

    def test_unknown_bit_is_reported(self):
        messages = decode_sudeban_error(32768)
        self.assertTrue(messages)
        self.assertTrue(any("Códigos desconocidos" in m for m in messages))

    def test_zero_code_returns_empty(self):
        self.assertEqual(decode_sudeban_error(0), [])

    def test_api_specific_date_field_messages(self):
        api01 = " | ".join(decode_sudeban_error(8388608, api="API-01"))
        api02 = " | ".join(decode_sudeban_error(8388608, api="API-02"))
        api03 = " | ".join(decode_sudeban_error(8388608, api="API-03"))
        api04 = " | ".join(decode_sudeban_error(8388608, api="API-04"))

        self.assertIn("Fecha Intervención", api01)
        self.assertIn("Fecha Subasta", api02)
        self.assertIn("Fecha Subasta", api03)
        self.assertIn("Fecha Pacto", api04)
