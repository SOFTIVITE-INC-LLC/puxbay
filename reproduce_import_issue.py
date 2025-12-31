
import os
import django
import sys
import unittest
from unittest.mock import MagicMock, patch
import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from branches.services.inventory import InventoryService
from accounts.models import Tenant, Branch
from main.models import Product, Category

class TestProductImport(unittest.TestCase):
    def setUp(self):
        # Create dummy tenant and branch
        self.tenant = Tenant(id='test-tenant-id', name='Test Tenant')
        self.branch = Branch(id='test-branch-id', name='Test Branch', tenant=self.tenant)
        self.service = InventoryService(self.tenant, self.branch)

    @patch('main.models.Product.objects.update_or_create')
    @patch('main.models.Category.objects.get_or_create')
    def test_import_valid_row(self, mock_get_or_create_category, mock_update_or_create_product):
        # Mock returns
        mock_category = Category(name='Test Cat')
        mock_get_or_create_category.return_value = (mock_category, True)
        mock_update_or_create_product.return_value = (Product(name='Test Product'), True)

        # 0: Name, 1: SKU, 2: Category, 3: Price, 4: Wholesale, 5: MinQty, 6: Cost, 
        # 7: Stock, 8: LowStock, 9: Barcode, 10: Expiry, ...
        row = [
            'Test Product', 'SKU001', 'General', '10.00', '8.00', '5', '5.00', 
            '100', '10', '123456', '2025-12-31', 'BATCH01', 'INV123', 'Desc', 
            'TRUE', '', '', '', '', ''
        ]
        
        success, message = self.service.import_row(row, 2)
        print(f"Valid Row Test: Success={success}, Message={message}")
        self.assertTrue(success)

    @patch('main.models.Product.objects.update_or_create')
    def test_import_missing_sku(self, mock_update_or_create):
        row = ['Test Product', '', 'General', '10.0'] # Missing SKU
        success, message = self.service.import_row(row, 3)
        print(f"Missing SKU Test: Success={success}, Message={message}")
        self.assertFalse(success)
        self.assertIn("Name and SKU are required", message)

    @patch('main.models.Product.objects.update_or_create')
    @patch('main.models.Category.objects.get_or_create')
    def test_excel_serial_date(self, mock_get_or_create_cat, mock_update_or_create):
         # Mock returns
        mock_category = Category(name='Test Cat')
        mock_get_or_create_cat.return_value = (mock_category, True)
        mock_update_or_create.return_value = (Product(name='Test Product'), True)

        # Excel often exports dates as floats like 45290.0 instead of "2023-12-31"
        row = [
            'Date Test', 'SKU002', 'General', '10', '8', '5', '5', 
            '100', '10', '123456', '45290.0', 'BATCH', 'INV', 'Desc', 'TRUE'
        ]
        
        success, message = self.service.import_row(row, 4)
        print(f"Serial Date Test: Success={success}, Message={message}")
        
        # Now we can verify the product has the date (mocked update_or_create)
        # However, since we mock update_or_create, we can check the call args if we wanted to be strict.
        # But specifically, we want to ensure no crash.
        self.assertTrue(success)

    @patch('main.models.Product.objects.update_or_create')
    def test_short_row(self, mock_update):
        row = ['Name', 'SKU'] # Too short
        success, message = self.service.import_row(row, 5)
        print(f"Short Row Test: Success={success}, Message={message}")
        self.assertFalse(success)
        self.assertIn("Incomplete data", message)

if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
