"""
Management command to cleanup old audit logs based on retention policy.

Usage:
    python manage.py cleanup_audit_logs --days=90
    python manage.py cleanup_audit_logs --days=30 --dry-run
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import AuditLog, APIRequestLog
from main.models import ProductHistory


class Command(BaseCommand):
    help = 'Delete audit logs older than specified days'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Delete logs older than this many days (default: 90)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['audit', 'api', 'product', 'all'],
            default='all',
            help='Which logs to clean up (default: all)'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        model_type = options['model']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(
            self.style.WARNING(
                f'{"[DRY RUN] " if dry_run else ""}Deleting logs older than {days} days '
                f'(before {cutoff_date.strftime("%Y-%m-%d %H:%M:%S")})'
            )
        )
        
        total_deleted = 0
        
        # Cleanup AuditLog
        if model_type in ['audit', 'all']:
            audit_count = AuditLog.objects.filter(timestamp__lt=cutoff_date).count()
            self.stdout.write(f'  AuditLog: {audit_count:,} records')
            
            if not dry_run:
                deleted = AuditLog.objects.filter(timestamp__lt=cutoff_date).delete()
                total_deleted += deleted[0]
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Deleted {deleted[0]:,} AuditLog records')
                )
        
        # Cleanup APIRequestLog
        if model_type in ['api', 'all']:
            api_count = APIRequestLog.objects.filter(timestamp__lt=cutoff_date).count()
            self.stdout.write(f'  APIRequestLog: {api_count:,} records')
            
            if not dry_run:
                deleted = APIRequestLog.objects.filter(timestamp__lt=cutoff_date).delete()
                total_deleted += deleted[0]
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Deleted {deleted[0]:,} APIRequestLog records')
                )
        
        # Cleanup ProductHistory
        if model_type in ['product', 'all']:
            product_count = ProductHistory.objects.filter(changed_at__lt=cutoff_date).count()
            self.stdout.write(f'  ProductHistory: {product_count:,} records')
            
            if not dry_run:
                deleted = ProductHistory.objects.filter(changed_at__lt=cutoff_date).delete()
                total_deleted += deleted[0]
                self.stdout.write(
                    self.style.SUCCESS(f'    ✓ Deleted {deleted[0]:,} ProductHistory records')
                )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'\n[DRY RUN] Would delete {audit_count + api_count + product_count:,} total records'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Successfully deleted {total_deleted:,} total records'
                )
            )
