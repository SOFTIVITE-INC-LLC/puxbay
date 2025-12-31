import requests
import datetime
from django.core.files.base import ContentFile
from django.db import transaction
from main.models import Product, Category

class InventoryService:
    def __init__(self, tenant, branch):
        self.tenant = tenant
        self.branch = branch

    def import_from_parser(self, parser):
        """
        Processes product import from an XLSXParser instance.
        """
        success_count = 0
        skip_count = 0
        errors = []
        
        data_iter = parser.parse()
        next(data_iter, None) # Skip header

        for row_idx, row in enumerate(data_iter, start=2):
            success, result_signal = self.import_row(row, row_idx)
            
            # If result_signal starts with 'skipped_', it was a skip
            if success and result_signal and str(result_signal).startswith('skipped_'):
                skip_count += 1
                if skip_count <= 5: # Only collect first 5 previews
                    errors.append(f"Diagnostic (Row {row_idx}): {result_signal}")
            elif success and result_signal == 'imported':
                success_count += 1
            else:
                errors.append(result_signal)
        
        return {
            'success': success_count,
            'skipped': skip_count,
            'errors': errors
        }

    def import_row(self, row, row_idx):
        """
        Imports a single product row. Returns (success, error_message).
        """
        try:
            if not row or len(row) < 4: 
                return False, f"Row {row_idx}: Incomplete data"
            
            # Extract and clean fields
            name = str(row[0]).strip() if len(row) > 0 else ''
            sku = str(row[1]).strip() if len(row) > 1 else ''
            cat_name = str(row[2]).strip() if len(row) > 2 else ''
            
            # Skip completely empty rows (common in Excel files)
            if not name and not sku and not cat_name:
                row_preview = "|".join([str(c) for c in row[:5]])
                return True, f"skipped_{row_preview}"
            
            if not name or not sku: 
                fields_found = []
                if name: fields_found.append(f"Name='{name}'")
                if sku: fields_found.append(f"SKU='{sku}'")
                found_str = ", ".join(fields_found) if fields_found else "both empty"
                return False, f"Row {row_idx}: Name and SKU are required (Found: {found_str})"
            
            # Critical: Ensure price is assigned!
            price = self._clean_float(row[3]) if len(row) > 3 else 0.0
            
            wholesale = self._clean_float(row[4]) if len(row) > 4 else 0.0
            min_qty = self._clean_int(row[5]) if len(row) > 5 else 1
            cost = self._clean_float(row[6]) if len(row) > 6 else 0.0
            stock = self._clean_int(row[7]) if len(row) > 7 else 0
            low_stock = self._clean_int(row[8]) if len(row) > 8 else 10
            barcode = str(row[9]).strip() if len(row) > 9 else ''
            expiry_str = str(row[10]).strip() if len(row) > 10 else ''
            batch = str(row[11]).strip() if len(row) > 11 else ''
            invoice = str(row[12]).strip() if len(row) > 12 else ''
            desc = str(row[13]).strip() if len(row) > 13 else ''
            active_str = str(row[14]).strip().upper() if len(row) > 14 else 'TRUE'
            image_url = str(row[15]).strip() if len(row) > 15 else ''
            
            # Extended Manufacturing Data
            mfg_date_str = str(row[16]).strip() if len(row) > 16 else ''
            country_origin = str(row[17]).strip() if len(row) > 17 else ''
            mfg_name = str(row[18]).strip() if len(row) > 18 else ''
            mfg_address = str(row[19]).strip() if len(row) > 19 else ''

            # Process Category
            category = None
            if cat_name:
                category, _ = Category.objects.get_or_create(
                    branch=self.branch,
                    name__iexact=cat_name,
                    defaults={'name': cat_name, 'tenant': self.tenant}
                )
            
            # Process Expiry
            expiry_date = self._parse_excel_date(expiry_str)
            update_expiry = expiry_date is not None

            is_active = active_str in ['TRUE', '1', 'YES', 'T']

            # Process Manufacturing Date (Optional)
            mfg_date = self._parse_excel_date(mfg_date_str)
            update_mfg = mfg_date is not None

            # Update or Create Product
            defaults = {
                'name': name,
                'category': category,
                'price': price,
                'wholesale_price': wholesale,
                'minimum_wholesale_quantity': min_qty,
                'cost_price': cost,
                'stock_quantity': stock,
                'low_stock_threshold': low_stock,
                'barcode': barcode,
                'batch_number': batch,
                'invoice_waybill_number': invoice,
                'description': desc,
                'is_active': is_active,
                'tenant': self.tenant
            }
            
            if update_expiry:
                defaults['expiry_date'] = expiry_date
            
            if update_mfg:
                defaults['manufacturing_date'] = mfg_date
                
            if country_origin:
                defaults['country_of_origin'] = country_origin
            if mfg_name:
                defaults['manufacturer_name'] = mfg_name
            if mfg_address:
                defaults['manufacturer_address'] = mfg_address

            with transaction.atomic():
                try:
                    product, created = Product.objects.update_or_create(
                        branch=self.branch,
                        sku=sku,
                        defaults=defaults
                    )
                except Exception as db_err:
                    from django.db import connections
                    db_info = f"Available Connections: {list(connections.databases.keys())}"
                    raise Exception(f"DATABASE ERROR: {str(db_err)} | {db_info}")

                if image_url and image_url.startswith('http'):
                    # Optimized download with shorter timeout to prevent Daphne timeout
                    self._download_product_image(product, image_url)

            return True, 'imported'
            
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            return False, f"Row {row_idx}: {str(e)} | Trace: {tb}"

    def _download_product_image(self, product, url):
        """
        Internal helper to download and save product images.
        Uses a short timeout to prevent blocking the import process.
        """
        try:
            # Shortened timeout to prevent worker killing (Daphne/Gunicorn)
            img_response = requests.get(url, timeout=3)
            if img_response.status_code == 200:
                ext = url.split('.')[-1].split('?')[0].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'webp', 'gif']:
                    ext = 'jpg'
                filename = f"{product.sku}.{ext}"
                product.image.save(filename, ContentFile(img_response.content), save=True)
        except Exception as img_err:
            # Non-blocking error logging
            pass

    def _clean_float(self, val):
        try: return float(str(val).strip()) 
        except: return 0.0
    
    def _clean_int(self, val):
        try: return int(float(str(val).strip()))
        except: return 0

    def _parse_excel_date(self, date_val):
        """
        Parses date from string ("2023-12-31") or Excel serial float (45290.0).
        """
        if not date_val:
            return None
            
        str_val = str(date_val).strip()
        if not str_val:
            return None

        # 1. Try generic string formats
        for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y', '%Y/%m/%d', '%d.%m.%Y']:
            try:
                return datetime.datetime.strptime(str_val, fmt).date()
            except ValueError:
                continue
        
        # 2. Try Excel Serial Date (days since 1899-12-30)
        try:
            # Excel base date is usually Dec 30 1899 for Mac/Windows compatibility
            serial = float(str_val)
            if serial > 30000: # Sanity check: 30000 is around year 1982, avoid small ints being treated as dates
                base_date = datetime.date(1899, 12, 30)
                delta = datetime.timedelta(days=serial)
                return base_date + delta
        except (ValueError, OverflowError):
            pass
            
        return None
