from django.core.management.base import BaseCommand
from main.tasks import nightly_inventory_analysis

class Command(BaseCommand):
    help = 'Manually triggers the AI Inventory Analysis for all tenants'

    def handle(self, *args, **options):
        self.stdout.write("Starting AI Inventory Analysis...")
        results = nightly_inventory_analysis()
        for result in results:
            self.stdout.write(f"Tenant: {result['tenant']}")
            for branch_res in result['analysis']:
                self.stdout.write(f"  Branch: {branch_res['branch']}")
                self.stdout.write(f"    Processed: {branch_res['processed_count']}")
                self.stdout.write(f"    Recommendations: {branch_res['recommendations_created']}")
        self.stdout.write(self.style.SUCCESS("Analysis complete."))
