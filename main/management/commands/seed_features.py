from django.core.management.base import BaseCommand
from billing.models import FeatureCategory, FeatureItem

class Command(BaseCommand):
    help = 'Seeds initial features into the database'

    def handle(self, *args, **options):
        feature_data = [
            {
                "name": "Core Operations",
                "icon": "grid_view",
                "order": 1,
                "features": [
                    {"title": "Point of Sale (POS)", "desc": "Fast, offline-first terminal with barcode support and split payments.", "icon": "point_of_sale", "order": 1},
                    {"title": "Inventory Control", "desc": "Real-time stock tracking with multi-branch synchronization and alerts.", "icon": "inventory_2", "order": 2},
                    {"title": "Multi-Branch Hub", "desc": "Manage unlimited locations and warehouses from a single dashboard.", "icon": "hub", "order": 3},
                    {"title": "Offline Sales", "desc": "Sell without internet; automatic cloud sync when connection returns.", "icon": "wifi_off", "order": 4},
                    {"title": "Multi-Currency", "desc": "Sell in any local or global currency with automatic conversion rates.", "icon": "currency_exchange", "order": 5},
                ]
            },
            {
                "name": "Intelligence & Analytics",
                "icon": "auto_graph",
                "order": 2,
                "features": [
                    {"title": "Stock Forecasting", "desc": "AI-driven predictions on when your products will run out.", "icon": "insights", "order": 1},
                    {"title": "Staff Leaderboards", "desc": "Gamify sales with real-time performance rankings and metrics.", "icon": "military_tech", "order": 2},
                    {"title": "Financial P&L", "desc": "Automatic Profit & Loss generation across all your branches.", "icon": "payments", "order": 3},
                    {"title": "Sales Heatmaps", "desc": "Visualize peak selling times and most profitable locations.", "icon": "query_stats", "order": 4},
                ]
            },
            {
                "name": "Customer Growth",
                "icon": "groups",
                "order": 3,
                "features": [
                    {"title": "Loyalty Program", "desc": "Points-based rewards to build long-term customer relationships.", "icon": "loyalty", "order": 1},
                    {"title": "Marketing Campaigns", "desc": "SMS and Email marketing directly from your dashboard.", "icon": "campaign", "order": 2},
                    {"title": "Digital Wallet", "desc": "PWA-based customer wallet for seamless cashless transactions.", "icon": "wallet", "order": 3},
                    {"title": "Feedback Loop", "desc": "Direct branch-level feedback to monitor customer satisfaction.", "icon": "reviews", "order": 4},
                ]
            },
            {
                "name": "Workforce & Operations",
                "icon": "engineering",
                "order": 4,
                "features": [
                    {"title": "Kitchen Kanban", "desc": "Live order tracking for cafes and restaurants with status updates.", "icon": "view_kanban", "order": 1},
                    {"title": "Staff Portal", "desc": "Dedicated workspace for employees to check tasks and schedules.", "icon": "person_celebrate", "order": 2},
                    {"title": "Time Clock", "desc": "Biometric or app-based attendance tracking with geofencing.", "icon": "schedule", "order": 3},
                    {"title": "Shift Rota", "desc": "Drag-and-drop scheduling for complex team rotations.", "icon": "calendar_month", "order": 4},
                ]
            },
            {
                "name": "Supply Chain",
                "icon": "local_shipping",
                "order": 5,
                "features": [
                    {"title": "Purchase Orders", "desc": "Streamlined procurement workflow from draft to fulfillment.", "icon": "shopping_cart_checkout", "order": 1},
                    {"title": "Supplier Portal", "desc": "Dedicated access for vendors to manage your purchase orders.", "icon": "contact_page", "order": 2},
                    {"title": "Stock Transfers", "desc": "Securely move inventory between locations with full audits.", "icon": "swap_horiz", "order": 3},
                    {"title": "Barcode Hub", "desc": "Bulk generate and print labels for your entire inventory.", "icon": "barcode_scanner", "order": 4},
                ]
            },
        ]

        for cat_data in feature_data:
            category, created = FeatureCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "icon": cat_data["icon"],
                    "order": cat_data["order"]
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            
            for item_data in cat_data["features"]:
                item, item_created = FeatureItem.objects.get_or_create(
                    category=category,
                    title=item_data["title"],
                    defaults={
                        "desc": item_data["desc"],
                        "icon": item_data["icon"],
                        "order": item_data["order"]
                    }
                )
                if item_created:
                    self.stdout.write(self.style.SUCCESS(f'  Created feature: {item.title}'))

        self.stdout.write(self.style.SUCCESS('Successfully seeded features'))
