import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from documentation.models import DocumentationSection, DocumentationArticle

def populate():
    print("Populating User Manual...")
    
    # Clear existing to avoid duplicates if re-run
    DocumentationSection.objects.all().delete()
    
    # 1. Introduction
    intro_sec = DocumentationSection.objects.create(title="Introduction", order=1, icon="info")
    DocumentationArticle.objects.create(
        section=intro_sec,
        title="Welcome",
        slug="welcome",
        order=1,
        content="""
        <p class="text-lg text-slate-600 mb-4">
            Welcome to the Puxbay System User Manual. This guide is designed to help you get up and running quickly and make the most of our powerful features. Whether you are a small boutique or a multi-store retail chain, our system scales with you.
        </p>
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r-md">
            <div class="flex">
                <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-blue-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd" />
                    </svg>
                </div>
                <div class="ml-3">
                    <p class="text-sm text-blue-700">
                        <strong>Tip:</strong> You can download this manual as a PDF by using your browser's print function (Ctrl+P).
                    </p>
                </div>
            </div>
        </div>
        """
    )
    
    # 2. Getting Started
    start_sec = DocumentationSection.objects.create(title="Getting Started", order=2, icon="rocket_launch")
    DocumentationArticle.objects.create(
        section=start_sec,
        title="Account Setup",
        slug="account-setup",
        order=1,
        content="""
        <h3 class="text-xl font-bold mb-2">Creating an Account</h3>
        <p class="mb-4">To begin, click the "Get Started" button on our homepage. You will need to provide your company name, email address, and a subdomain (e.g., <code>my-shop</code>) which will be your unique web address.</p>
        
        <h3 class="text-xl font-bold mb-2">Logging In</h3>
        <p>Once registered, navigate to your custom subdomain (e.g., <code>my-shop.possystem.com</code>) and log in with your credentials. You can access the Dashboard or the POS terminal directly.</p>
        """
    )
    
    DocumentationArticle.objects.create(
        section=start_sec,
        title="Branch Management",
        slug="branch-management",
        order=2,
        content="""
        <p>Our system supports multi-location businesses. To manage branches:</p>
        <ol class="list-decimal pl-5 space-y-2 mt-2">
            <li>Go to <strong>Branches</strong> in the sidebar.</li>
            <li>Click <strong>Add Branch</strong>.</li>
            <li>Enter the branch name (e.g., 'Downtown Store') and details.</li>
            <li>Managers can be assigned specifically to a branch.</li>
        </ol>
        """
    )
    
    # 3. Products & Inventory
    prod_sec = DocumentationSection.objects.create(title="Products & Inventory", order=3, icon="inventory_2")
    DocumentationArticle.objects.create(
        section=prod_sec,
        title="Managing Products",
        slug="managing-products",
        order=1,
        content="""
        <p class="mb-4">You can add products manually or import them.</p>
        
        <h4 class="font-bold">Manual Entry</h4>
        <p class="mb-2">Go to <strong>Products > Add New</strong>. Required fields:</p>
        <ul class="list-disc pl-5 mb-4">
            <li><strong>Name</strong>: Product title.</li>
            <li><strong>SKU</strong>: Unique Stock Keeping Unit.</li>
            <li><strong>Price</strong>: Selling price.</li>
            <li><strong>Stock</strong>: Initial quantity.</li>
        </ul>
        
        <h4 class="font-bold">Bulk Import</h4>
        <p>Go to the Product List page and click <strong>Import</strong>. Download the .xlsx template, fill it with your data, and upload it.</p>
        """
    )
    
    DocumentationArticle.objects.create(
        section=prod_sec,
        title="Inventory Control",
        slug="inventory-control",
        order=2,
        content="""
        <p>Inventory is tracked in real-time.</p>
        
        <h4 class="font-bold mt-4">Low Stock Alerts</h4>
        <p>Set a 'Low Stock Threshold' for items (e.g., 10). When stock dips below this, it appears on the dashboard alert list.</p>
        
        <h4 class="font-bold mt-4">Transfers</h4>
        <p>Move stock between branches using the <strong>Transfers</strong> menu. Creates a transfer record that must be 'Received' by the destination branch.</p>
        """
    )
    
    # 4. Sales (POS)
    pos_sec = DocumentationSection.objects.create(title="Sales (POS)", order=4, icon="point_of_sale")
    DocumentationArticle.objects.create(
        section=pos_sec,
        title="Processing a Sale",
        slug="processing-sale",
        order=1,
        content="""
        <p>The POS screen is optimized for speed.</p>
        <ol class="list-decimal pl-5 space-y-2 mt-2">
            <li><strong>Add Items</strong>: Scan a barcode or search by name.</li>
            <li><strong>Customer</strong>: (Optional) Search for a loyalty customer.</li>
            <li><strong>Discount</strong>: Click 'Discount' to apply a % off specific items or the cart.</li>
            <li><strong>Pay</strong>: Click Pay, select method (Cash/Card).</li>
        </ol>
        """
    )
    
    DocumentationArticle.objects.create(
        section=pos_sec,
        title="Offline Mode",
        slug="offline-mode",
        order=2,
        content="""
        <div class="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-r-md mb-4">
            <p class="text-sm text-yellow-700"><strong>Note:</strong> You must load the POS page while online once to cache data.</p>
        </div>
        <p>If internet is lost, the POS switches to Offline Mode automatically. Sales are stored locally in the browser.</p>
        <p class="mt-2">When connection returns, a <strong>Sync</strong> badge appears. Click it to upload pending transactions.</p>
        """
    )
    
    # 5. Reports
    rep_sec = DocumentationSection.objects.create(title="Reports & Analytics", order=5, icon="analytics")
    DocumentationArticle.objects.create(
        section=rep_sec,
        title="Available Reports",
        slug="available-reports",
        order=1,
        content="""
        <ul class="space-y-2">
            <li><strong>Sales Report</strong>: Revenue over time, profit margins.</li>
            <li><strong>Product Report</strong>: Best sellers, dead stock, inventory valuation.</li>
            <li><strong>Cashier Report</strong>: Staff performance tracking.</li>
        </ul>
        <p class="mt-4">All reports can be filtered by Date Range (Today, Week, Month, Custom).</p>
        """
    )

    print("Manual populated successfully!")

if __name__ == '__main__':
    populate()
