import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from billing.models import LegalDocument, BlogCategory, BlogTag, BlogPost
from documentation.models import DocumentationSection, DocumentationArticle

class Command(BaseCommand):
    help = 'Populates the database with realistic data for User Manual, Blog, and Legal pages'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating content...')
        
        # 1. Admin User
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create a superuser first.'))
            return

        # 2. Legal Documents
        self.stdout.write('Populating Legal Documents...')
        legal_docs = [
            {
                'title': 'Terms of Service',
                'slug': 'terms-of-service',
                'content': """
                    <h2>1. Welcome to Puxbay</h2>
                    <p>By using Puxbay, you agree to these terms. Our platform provides retail management solutions for businesses of all sizes.</p>
                    <h2>2. User Accounts</h2>
                    <p>Users are responsible for maintaining the security of their account credentials. Any activity under your account is your responsibility.</p>
                    <h2>3. Subscription and Billing</h2>
                    <p>Subscriptions are billed in advance on a monthly or yearly basis. Free trials are available for 7 days.</p>
                    <h2>4. Data Privacy</h2>
                    <p>Your data is yours. We do not sell your business data. Please refer to our Privacy Policy for more details.</p>
                """
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy-policy',
                'content': """
                    <h2>1. Data Collection</h2>
                    <p>We collect only the necessary data to provide our services, including business name, email, and transaction records.</p>
                    <h2>2. Cookies</h2>
                    <p>We use essential cookies to maintain your session and improve user experience.</p>
                    <h2>3. Third-Party Services</h2>
                    <p>We use Stripe and Paystack for payment processing. They collect relevant payment information as per their own policies.</p>
                """
            },
            {
                'title': 'Refund Policy',
                'slug': 'refund-policy',
                'content': """
                    <h2>1. 7-Day Money Back Guarantee</h2>
                    <p>We offer a full refund if requested within 7 days of your first subscription payment.</p>
                    <h2>2. Cancellation</h2>
                    <p>You can cancel your subscription at any time. You will continue to have access until the end of your current billing period.</p>
                """
            },
            {
                'title': 'Cookie Policy',
                'slug': 'cookie-policy',
                'content': """
                    <h2>1. What are cookies?</h2>
                    <p>Cookies are small text files stored on your device that help us recognize you when you return to our site.</p>
                    <h2>2. Types of Cookies We Use</h2>
                    <ul>
                        <li><b>Essential:</b> Necessary for logging in and security.</li>
                        <li><b>Analytics:</b> Helps us understand how you use our platform.</li>
                    </ul>
                """
            }
        ]
        
        for doc in legal_docs:
            LegalDocument.objects.update_or_create(
                slug=doc['slug'],
                defaults={'title': doc['title'], 'content': doc['content'], 'is_published': True}
            )

        # 3. Blog Content
        self.stdout.write('Populating Blog Content...')
        # Categories
        cat_ret, _ = BlogCategory.objects.get_or_create(name='Retail Strategy', defaults={'slug': 'retail-strategy'})
        cat_tech, _ = BlogCategory.objects.get_or_create(name='Technology', defaults={'slug': 'technology'})
        cat_bus, _ = BlogCategory.objects.get_or_create(name='Business Growth', defaults={'slug': 'business-growth'})

        # Tags
        tag_pos, _ = BlogTag.objects.get_or_create(name='POS', defaults={'slug': 'pos'})
        tag_inv, _ = BlogTag.objects.get_or_create(name='Inventory', defaults={'slug': 'inventory'})
        tag_sales, _ = BlogTag.objects.get_or_create(name='Sales', defaults={'slug': 'sales'})

        blog_posts = [
            {
                'title': '5 Ways to Boost Your Retail Sales in 2025',
                'slug': 'boost-retail-sales-2025',
                'excerpt': 'Discover the latest trends and strategies to drive more traffic and sales to your store.',
                'content': """
                    <p>The retail landscape is changing fast. Here are 5 strategies to stay ahead:</p>
                    <ol>
                        <li><b>Omnichannel Experience:</b> Sell online and offline seamlessly.</li>
                        <li><b>Personalized Marketing:</b> Use customer data to offer relevant deals.</li>
                        <li><b>Optimized Inventory:</b> Never run out of your best-sellers.</li>
                        <li><b>Loyalty Programs:</b> Reward your most frequent customers.</li>
                        <li><b>Fast Checkout:</b> Use a modern POS like Puxbay to reduce wait times.</li>
                    </ol>
                """,
                'category': cat_ret,
                'is_featured': True
            },
            {
                'title': 'Why Cloud-Based POS is a Game Changer',
                'slug': 'cloud-pos-game-changer',
                'excerpt': 'Learn why moving your point of sale to the cloud is the best decision for your business.',
                'content': """
                    <p>Legacy POS systems are a thing of the past. Cloud systems offer mobility, real-time data, and effortless updates.</p>
                    <p>Puxbay allows you to monitor your multiple branches from your phone, anywhere in the world.</p>
                """,
                'category': cat_tech,
                'is_featured': False
            },
            {
                'title': 'Mastering Inventory Management',
                'slug': 'mastering-inventory-management',
                'excerpt': 'Poor inventory management sinks businesses. Learn how to master yours.',
                'content': """
                    <p>Inventory management is more than just counting boxes. It's about forecasting demand and managing suppliers.</p>
                    <p>With Puxbay's advanced reporting, you can see exactly what is moving and what is sitting on your shelves.</p>
                """,
                'category': cat_bus,
                'is_featured': False
            }
        ]

        for post_data in blog_posts:
            post, created = BlogPost.objects.update_or_create(
                slug=post_data['slug'],
                defaults={
                    'title': post_data['title'],
                    'author': admin_user,
                    'excerpt': post_data['excerpt'],
                    'content': post_data['content'],
                    'category': post_data['category'],
                    'status': 'published',
                    'is_featured': post_data['is_featured'],
                    'published_at': timezone.now()
                }
            )
            post.tags.add(tag_pos, tag_inv, tag_sales)

        # 4. User Manual
        self.stdout.write('Populating User Manual...')
        manual_sections = [
            {
                'title': 'Getting Started',
                'order': 1,
                'icon': 'rocket_launch',
                'articles': [
                    {
                        'title': 'System Overview',
                        'slug': 'system-overview',
                        'content': '<p>Puxbay is an all-in-one retail management platform. It combines POS, inventory, staff management, and analytics into one seamless dashboard.</p>',
                        'order': 1
                    },
                    {
                        'title': 'First Login',
                        'slug': 'first-login',
                        'content': '<p>Log in with your provided credentials and set up your multi-factor authentication for added security.</p>',
                        'order': 2
                    }
                ]
            },
            {
                'title': 'Inventory Management',
                'order': 2,
                'icon': 'inventory_2',
                'articles': [
                    {
                        'title': 'Adding Products',
                        'slug': 'adding-products',
                        'content': '<p>Navigate to the products section and click "Add Product". You can add images, SKUs, and set categories.</p>',
                        'order': 1
                    },
                    {
                        'title': 'Stock Tracking',
                        'slug': 'stock-tracking',
                        'content': '<p>Enable low-stock alerts to be notified whenever an item falls below your specified threshold.</p>',
                        'order': 2
                    }
                ]
            },
            {
                'title': 'Sales & POS',
                'order': 3,
                'icon': 'point_of_sale',
                'articles': [
                    {
                        'title': 'Running the Terminal',
                        'slug': 'running-terminal',
                        'content': '<p>The POS terminal is offline-first. It will sync your sales to the cloud as soon as a connection is available.</p>',
                        'order': 1
                    }
                ]
            }
        ]

        for sec_data in manual_sections:
            section, _ = DocumentationSection.objects.update_or_create(
                title=sec_data['title'],
                defaults={'doc_type': 'manual', 'order': sec_data['order'], 'icon': sec_data['icon']}
            )
            for art_data in sec_data['articles']:
                DocumentationArticle.objects.update_or_create(
                    slug=art_data['slug'],
                    defaults={
                        'section': section,
                        'title': art_data['title'],
                        'content': art_data['content'],
                        'order': art_data['order'],
                        'is_published': True
                    }
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated all content!'))
