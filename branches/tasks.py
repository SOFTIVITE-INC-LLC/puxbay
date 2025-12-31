import logging
import base64
from celery import shared_task
from django.core.cache import cache
from django_tenants.utils import tenant_context
from accounts.models import Tenant, Branch
from .xlsx_utils import XLSXParser
from .services.inventory import InventoryService

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def import_products_task(self, tenant_id, branch_id, file_content):
    """
    Background task to import products from an XLSX file.
    file_content should be bytes or base64-encoded string
    """
    task_id = self.request.id
    cache_key = f"import_progress_{task_id}"
    
    progress = {
        'status': 'processing',
        'current': 0,
        'total': 0,
        'progress': 0,
        'success': 0,
        'total_errors': 0,
        'errors': []
    }
    cache.set(cache_key, progress, timeout=3600)

    try:
        # Handle base64-encoded content if needed
        if isinstance(file_content, str):
            try:
                file_content = base64.b64decode(file_content)
            except Exception as decode_err:
                logger.error(f"Failed to decode base64 content: {decode_err}")
                raise ValueError("Invalid file content encoding")
        
        tenant = Tenant.objects.get(id=tenant_id)
        with tenant_context(tenant):
            branch = Branch.objects.get(id=branch_id)
            logger.info(f"Starting import for branch: {branch.name}")
            
            # Parse the XLSX file
            try:
                parser = XLSXParser(file_content)
                data_generator = parser.parse()
            except Exception as parse_err:
                logger.error(f"Failed to parse XLSX file: {parse_err}")
                raise ValueError(f"Invalid XLSX file: {str(parse_err)}")
            
            # Convert to list to get total and avoid generator issues
            all_rows = list(data_generator)
            total_rows = len(all_rows) - 1 if len(all_rows) > 0 else 0
            
            logger.info(f"Found {total_rows} rows to process.")
            
            progress['total'] = total_rows
            cache.set(cache_key, progress, timeout=3600)
            
            # Simple iteration
            inventory_service = InventoryService(tenant=tenant, branch=branch)
            data_rows = all_rows[1:] if len(all_rows) > 1 else []
            
            for idx, row in enumerate(data_rows, start=1):
                try:
                    success, error = inventory_service.import_row(row, idx + 1)
                    
                    if success:
                        progress['success'] += 1
                    else:
                        progress['total_errors'] += 1
                        err_str = f"Row {idx+1}: {str(error)}"
                        progress['errors'].append(err_str)
                        if len(progress['errors']) > 10:
                            progress['errors'].pop(0)
                except Exception as row_err:
                    logger.error(f"Error processing row {idx+1}: {row_err}")
                    progress['total_errors'] += 1
                    progress['errors'].append(f"Row {idx+1}: {str(row_err)}")
                
                # Update progress
                progress['current'] = idx
                if total_rows > 0:
                    progress['progress'] = int((idx / total_rows) * 100)
                
                cache.set(cache_key, progress, timeout=3600)

            progress['status'] = 'completed'
            progress['progress'] = 100
            cache.set(cache_key, progress, timeout=3600)
            
            logger.info(f"Import completed: {progress['success']} success, {progress['total_errors']} errors")
            return {
                'success': progress['success'],
                'errors': progress['total_errors'],
                'task_id': task_id
            }

    except Exception as e:
        logger.exception(f"Error in import task: {e}")
        progress.update({
            'status': 'error',
            'message': str(e)
        })
        cache.set(cache_key, progress, timeout=3600)
        raise

