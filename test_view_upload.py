"""
Test the product import through the actual Django view (simulating web upload)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'possystem.settings')
django.setup()

from django.test import Client, RequestFactory
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from accounts.models import Tenant, Branch, UserProfile
from main.models import Product
from django_tenants.utils import tenant_context
import time

def test_view_upload():
    print("=" * 70)
    print("TESTING PRODUCT IMPORT THROUGH DJANGO VIEW")
    print("=" * 70)
    
    # Get tenant and branch
    tenant = Tenant.objects.get(schema_name='eduxkope')
    branch = Branch.objects.filter(tenant=tenant).first()
    
    print(f"\n✓ Tenant: {tenant.name}")
    print(f"✓ Branch: {branch.name}")
    
    # Get or create a user for this tenant
    user = User.objects.filter(username='admin').first()
    if not user:
        print("❌ Admin user not found!")
        return
    
    print(f"✓ User: {user.username}")
    
    # Get user profile
    profile = UserProfile.objects.filter(user=user, tenant=tenant).first()
    if not profile:
        print("❌ User profile not found for this tenant!")
        return
    
    print(f"✓ User Profile: {profile.role}")
    
    # Count products before
    with tenant_context(tenant):
        before_count = Product.objects.filter(branch=branch).count()
        print(f"\n📦 Products before upload: {before_count}")
    
    # Read the sample file
    if not os.path.exists('sample_products_300.xlsx'):
        print("❌ Sample file not found!")
        return
    
    with open('sample_products_300.xlsx', 'rb') as f:
        file_content = f.read()
    
    print(f"✓ Loaded sample file ({len(file_content)} bytes)")
    
    # Create a test client
    client = Client()
    
    # Login the user
    client.force_login(user)
    print("✓ User logged in")
    
    # Set the tenant in the session (simulate subdomain middleware)
    session = client.session
    session['tenant_id'] = str(tenant.id)
    session.save()
    
    # Create the uploaded file
    uploaded_file = SimpleUploadedFile(
        "test_products.xlsx",
        file_content,
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    # Make the POST request to the import view
    url = f'/branches/{branch.id}/products/import/'
    print(f"\n🚀 Posting to: {url}")
    print(f"   Host: {tenant.schema_name}.localhost")
    
    response = client.post(
        url,
        {
            'import_file': uploaded_file
        },
        HTTP_HOST=f'{tenant.schema_name}.localhost',  # Set the subdomain
        follow=False  # Don't follow redirects yet
    )
    
    print(f"✓ Response status: {response.status_code}")
    
    if response.status_code == 302:  # Redirect
        print(f"✓ Redirected to: {response.url}")
        
        # Check messages
        from django.contrib.messages import get_messages
        messages = list(get_messages(response.wsgi_request))
        print(f"\n💬 Messages ({len(messages)}):")
        for msg in messages:
            print(f"   [{msg.level_tag.upper()}] {msg.message}")
    else:
        print(f"❌ Unexpected status code: {response.status_code}")
        print(f"   Response: {response.content[:500]}")
    
    # Wait a bit for Celery to process (if async)
    print("\n⏳ Waiting 15 seconds for Celery to process...")
    time.sleep(15)
    
    # Count products after
    with tenant_context(tenant):
        after_count = Product.objects.filter(branch=branch).count()
        print(f"\n📦 Products after upload: {after_count}")
        print(f"✅ New products imported: {after_count - before_count}")
        
        if after_count > before_count:
            print("\n🎉 SUCCESS! Products were imported through the view!")
            print("\n📋 Sample of newly imported products:")
            recent = Product.objects.filter(branch=branch).order_by('-created_at')[:5]
            for p in recent:
                print(f"   - {p.name} (SKU: {p.sku}, Price: ${p.price})")
        else:
            print("\n❌ No new products were imported!")
            print("   Check the Celery worker logs for errors.")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    test_view_upload()
