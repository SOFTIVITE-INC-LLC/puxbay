from django.core.management.base import BaseCommand
from main.models import DatabaseBackup
from django.conf import settings
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Syncs backup files from disk to the database'

    def handle(self, *args, **options):
        # Define backup directory (adjust path as needed, matching your deploy script)
        BACKUP_DIR = "/opt/puxbay/backups/postgres" 
        
        # Ensure directory exists (for local testing flexibility)
        if not os.path.exists(BACKUP_DIR):
             # Fallback for development if needed, or just warn
             self.stdout.write(self.style.WARNING(f"Backup directory {BACKUP_DIR} does not exist."))
             return

        self.stdout.write(f"Scanning {BACKUP_DIR} for backups...")

        # Get all .sql.gz files
        files = [f for f in os.listdir(BACKUP_DIR) if f.endswith('.sql.gz')]
        
        # Track existing records to detect deletions
        existing_filenames = set(DatabaseBackup.objects.values_list('filename', flat=True))
        found_filenames = set(files)

        # 1. Add new files
        for filename in files:
            if filename not in existing_filenames:
                file_path = os.path.join(BACKUP_DIR, filename)
                try:
                    stats = os.stat(file_path)
                    DatabaseBackup.objects.create(
                        filename=filename,
                        file_path=file_path,
                        size_bytes=stats.st_size,
                        created_at=datetime.fromtimestamp(stats.st_mtime)
                    )
                    self.stdout.write(self.style.SUCCESS(f"Registered: {filename}"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to register {filename}: {e}"))

        # 2. Remove deleted files from DB
        to_delete = existing_filenames - found_filenames
        if to_delete:
            DatabaseBackup.objects.filter(filename__in=to_delete).delete()
            self.stdout.write(self.style.WARNING(f"Removed {len(to_delete)} missing records."))

        self.stdout.write(self.style.SUCCESS("Sync complete."))
