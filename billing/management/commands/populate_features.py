from django.core.management.base import BaseCommand
from billing.models import FeatureCategory, FeatureItem

class Command(BaseCommand):
    help = 'Populate the database with system features from views.py fallback'

    def handle(self, *args, **options):
        feature_data = [
            {
                "name": "Omnichannel Sales",
                "icon": "storefront",
                "features": [
                    {"title": "Unified POS", "desc": "Fast, offline-first terminal with barcode support, kitchen routing, and split payments.", "icon": "point_of_sale"},
                    {"title": "E-commerce Storefront", "desc": "Self-hosted online store with real-time inventory sync and secure checkout.", "icon": "shopping_bag"},
                    {"title": "Self-Service Kiosk", "desc": "Interactive kiosk mode for self-checkout and digital menu ordering.", "icon": "settings_remote"},
                    {"title": "Mobile Wallet", "desc": "PWA-based customer wallet for cashless payments and loyalty tracking.", "icon": "account_balance_wallet"},
                    {"title": "Offline Sync", "desc": "Sell without internet; automatic background sync when connection returns.", "icon": "cloud_sync"},
                ]
            },
            {
                "name": "Inventory & Supply Chain",
                "icon": "inventory",
                "features": [
                    {"title": "Global Inventory", "desc": "Real-time stock tracking across unlimited branches and warehouses.", "icon": "inventory_2"},
                    {"title": "Supplier Portal", "desc": "Dedicated vendor access for automated procurement and PO fulfillment.", "icon": "precision_manufacturing"},
                    {"title": "Stock Transfers", "desc": "Secure inventory movements between locations with dual-confirmation audits.", "icon": "swap_horiz"},
                    {"title": "Barcode Engine", "desc": "Bulk generate, customize, and print labels for every product in your catalog.", "icon": "barcode_scanner"},
                    {"title": "Purchase Orders", "desc": "Complete workflow from draft to receiving with automated stock updating.", "icon": "shopping_cart_checkout"},
                ]
            },
            {
                "name": "Business Intelligence",
                "icon": "auto_graph",
                "features": [
                    {"title": "Stock Forecasting", "desc": "AI-driven algorithms predicting stockouts based on local sales velocity.", "icon": "insights"},
                    {"title": "Real-time Analytics", "desc": "Comprehensive dashboards for sales trends, top products, and revenue.", "icon": "analytics"},
                    {"title": "Sales Heatmaps", "desc": "Visualize peak hours and busiest locations with geographical heatmapping.", "icon": "query_stats"},
                    {"title": "Custom Reports", "desc": "Drag-and-drop report builder to export any metric as CSV or PDF.", "icon": "table_chart"},
                    {"title": "Global Command Center", "desc": "Manage pricing and permissions for 100+ branches from one seat.", "icon": "admin_panel_settings"},
                ]
            },
            {
                "name": "Customer Experience",
                "icon": "volunteer_activism",
                "features": [
                    {"title": "Tiered Loyalty", "desc": "Gamify shopping with points, custom tiers, and exclusive member discounts.", "icon": "style"},
                    {"title": "Marketing Hub", "desc": "Broadcast SMS and Email campaigns targeted by customer purchase history.", "icon": "campaign"},
                    {"title": "Feedback Engine", "desc": "Collect and analyze branch-level customer satisfaction scores in real-time.", "icon": "rate_review"},
                    {"title": "Returns & Refunds", "desc": "Managed workflow for item returns, restocking, and automated refunds.", "icon": "assignment_return"},
                    {"title": "CRM Dashboard", "desc": "360° view of customer spending, behavior, and lifecycle management.", "icon": "groups"},
                ]
            },
            {
                "name": "Workforce & ERP",
                "icon": "work_history",
                "features": [
                    {"title": "Biometric Attendance", "desc": "Staff clock-in/out with geofencing and comprehensive attendance reports.", "icon": "schedule"},
                    {"title": "Commission System", "desc": "Rules-based salesperson commissions calculated automatically on every sale.", "icon": "paid"},
                    {"title": "Expense Tracking", "desc": "Log and categorize business overheads with multi-branch allocation.", "icon": "receipt_long"},
                    {"title": "Kitchen Display", "desc": "Kanban-style digital order management for bars and restaurants.", "icon": "view_kanban"},
                    {"title": "2FA Security", "desc": "Enterprise-grade protection with TOTP-based two-factor authentication.", "icon": "verified_user"},
                ]
            },
        ]

        total_categories = 0
        total_items = 0

        for cat_data in feature_data:
            category, created = FeatureCategory.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "icon": cat_data["icon"],
                    "order": total_categories * 10
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category.name}'))
            total_categories += 1

            for item_idx, item_data in enumerate(cat_data["features"]):
                item, item_created = FeatureItem.objects.get_or_create(
                    category=category,
                    title=item_data["title"],
                    defaults={
                        "desc": item_data["desc"],
                        "icon": item_data["icon"],
                        "order": item_idx * 10
                    }
                )
                if item_created:
                    total_items += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully populated {total_categories} categories and {total_items} feature items.'))
