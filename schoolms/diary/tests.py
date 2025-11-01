"""Pagrindiniai testų šablonai."""
from django.test import TestCase


class PavyzdzioTestas(TestCase):
    """Minimalus pavyzdinis testas, kad struktūra būtų paruošta."""

    def test_pagrindinis(self) -> None:
        self.assertTrue(True)
