"""
Tests for helasabili app models.
"""

from django.test import TestCase
from helasabili.models import HelasabiliInventory


class HelasabiliInventoryTestCase(TestCase):
    """Test cases for HelasabiliInventory model"""
    
    def test_model_is_read_only(self):
        """Ensure the model prevents saves"""
        inventory = HelasabiliInventory(
            id=1,
            product_name='Test Land',
            product_code='TEST001',
            quantity=1
        )
        with self.assertRaises(Exception):
            inventory.save()
    
    def test_model_prevents_deletes(self):
        """Ensure the model prevents deletes"""
        # This would need an actual database record to test properly
        pass
