from django.core.management.base import BaseCommand
from billing.models import PricingPlan, PlanFeature, FAQ


class Command(BaseCommand):
    help = 'Populate pricing page with test data'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("POPULATING PRICING PAGE DATA")
        self.stdout.write("=" * 60)
        
        # Clear existing data
        self.stdout.write("\nClearing existing data...")
        PlanFeature.objects.all().delete()
        PricingPlan.objects.all().delete()
        FAQ.objects.all().delete()
        
        # Populate pricing plans
        plans_count, features_count = self.populate_pricing_plans()
        
        # Populate FAQs
        faqs_count = self.populate_faqs()
        
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("SUMMARY")
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(f"[OK] Pricing Plans: 4 plans created"))
        self.stdout.write(self.style.SUCCESS(f"[OK] Plan Features: {features_count} features created"))
        self.stdout.write(self.style.SUCCESS(f"[OK] FAQs: {faqs_count} FAQs created"))
        self.stdout.write("\n" + self.style.SUCCESS("[OK] Pricing page data population complete!"))
        self.stdout.write("=" * 60)

    def populate_pricing_plans(self):
        """Populate PricingPlan and PlanFeature models"""
        
        plans_data = [
            {
                'name': 'Starter',
                'slug': 'starter',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'currency': 'USD',
                'description': 'Perfect for small businesses just getting started with their first location.',
                'is_popular': False,
                'button_text': 'Start Free Trial',
                'order': 1,
                'features': [
                    {'text': '1 Branch Location', 'is_available': True},
                    {'text': 'Up to 5 Staff Members', 'is_available': True},
                    {'text': 'Basic Inventory Management', 'is_available': True},
                    {'text': 'Point of Sale (POS)', 'is_available': True},
                    {'text': 'Basic Reporting', 'is_available': True},
                    {'text': 'Email Support', 'is_available': True},
                    {'text': 'Mobile App Access', 'is_available': True},
                    {'text': 'Advanced Analytics', 'is_available': False},
                    {'text': 'API Access', 'is_available': False},
                    {'text': 'Priority Support', 'is_available': False},
                ]
            },
            {
                'name': 'Professional',
                'slug': 'professional',
                'price_monthly': 79.99,
                'price_yearly': 799.99,
                'currency': 'USD',
                'description': 'Ideal for growing businesses with multiple locations and advanced needs.',
                'is_popular': True,
                'button_text': 'Start Free Trial',
                'order': 2,
                'features': [
                    {'text': 'Up to 5 Branch Locations', 'is_available': True},
                    {'text': 'Up to 20 Staff Members', 'is_available': True},
                    {'text': 'Advanced Inventory Management', 'is_available': True},
                    {'text': 'Multi-Location POS', 'is_available': True},
                    {'text': 'Advanced Reporting & Analytics', 'is_available': True},
                    {'text': 'Priority Email Support', 'is_available': True},
                    {'text': 'Mobile App Access', 'is_available': True},
                    {'text': 'Customer Loyalty Program', 'is_available': True},
                    {'text': 'Stock Transfer Between Branches', 'is_available': True},
                    {'text': 'API Access (1,000 req/day)', 'is_available': True},
                ]
            },
            {
                'name': 'Enterprise',
                'slug': 'enterprise',
                'price_monthly': 199.99,
                'price_yearly': 1999.99,
                'currency': 'USD',
                'description': 'For large organizations requiring maximum flexibility and unlimited scale.',
                'is_popular': False,
                'button_text': 'Contact Sales',
                'order': 3,
                'features': [
                    {'text': 'Unlimited Branch Locations', 'is_available': True},
                    {'text': 'Unlimited Staff Members', 'is_available': True},
                    {'text': 'Enterprise Inventory Management', 'is_available': True},
                    {'text': 'Multi-Location POS', 'is_available': True},
                    {'text': 'Custom Reporting & Analytics', 'is_available': True},
                    {'text': '24/7 Priority Support', 'is_available': True},
                    {'text': 'Mobile App Access', 'is_available': True},
                    {'text': 'Advanced Customer CRM', 'is_available': True},
                    {'text': 'Custom Integrations', 'is_available': True},
                    {'text': 'Unlimited API Access', 'is_available': True},
                    {'text': 'Dedicated Account Manager', 'is_available': True},
                    {'text': 'SLA Guarantee', 'is_available': True},
                ]
            },
            {
                'name': 'Developer',
                'slug': 'developer',
                'price_monthly': 49.99,
                'price_yearly': 499.99,
                'currency': 'USD',
                'description': 'Build custom solutions and integrations on our platform with full API access.',
                'is_popular': False,
                'button_text': 'Get API Key',
                'order': 4,
                'features': [
                    {'text': '1 Sandbox Branch', 'is_available': True},
                    {'text': '2 Developer Accounts', 'is_available': True},
                    {'text': 'Full API Documentation', 'is_available': True},
                    {'text': 'Webhook Support', 'is_available': True},
                    {'text': 'API Access (5,000 req/day)', 'is_available': True},
                    {'text': 'Developer Discord Community', 'is_available': True},
                    {'text': 'SDK & Code Examples', 'is_available': True},
                    {'text': 'Sandbox Environment', 'is_available': True},
                    {'text': 'Technical Documentation', 'is_available': True},
                    {'text': 'Email Support', 'is_available': True},
                ]
            }
        ]
        
        created_features = 0
        
        for plan_data in plans_data:
            features_data = plan_data.pop('features')
            
            plan = PricingPlan.objects.create(**plan_data)
            self.stdout.write(self.style.SUCCESS(f"[OK] Created plan: {plan.name}"))
            
            # Create features for this plan
            for idx, feature_data in enumerate(features_data):
                PlanFeature.objects.create(
                    plan=plan,
                    text=feature_data['text'],
                    is_available=feature_data['is_available'],
                    order=idx
                )
                created_features += 1
        
        return len(plans_data), created_features

    def populate_faqs(self):
        """Populate FAQ model"""
        
        faqs_data = [
            {
                'question': 'What is included in the free trial?',
                'answer': 'All plans come with a 14-day free trial that includes full access to all features of your chosen plan. No credit card required to start your trial.',
                'order': 1,
            },
            {
                'question': 'Can I change my plan later?',
                'answer': 'Yes! You can upgrade or downgrade your plan at any time. When you upgrade, you\'ll get immediate access to new features. When you downgrade, changes take effect at the end of your current billing period.',
                'order': 2,
            },
            {
                'question': 'What payment methods do you accept?',
                'answer': 'We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and for customers in select regions, we also support mobile money and bank transfers via Paystack.',
                'order': 3,
            },
            {
                'question': 'Is there a setup fee?',
                'answer': 'No, there are no setup fees or hidden charges. You only pay the monthly or annual subscription fee for your chosen plan.',
                'order': 4,
            },
            {
                'question': 'Can I cancel my subscription anytime?',
                'answer': 'Yes, you can cancel your subscription at any time. Your account will remain active until the end of your current billing period, and you won\'t be charged again.',
                'order': 5,
            },
            {
                'question': 'Do you offer discounts for annual billing?',
                'answer': 'Yes! When you choose annual billing, you save approximately 17% compared to paying monthly. That\'s like getting 2 months free!',
                'order': 6,
            },
            {
                'question': 'What happens if I exceed my plan limits?',
                'answer': 'If you approach your plan limits (branches, users, or API calls), we\'ll notify you in advance. You can then upgrade to a higher plan to continue without interruption.',
                'order': 7,
            },
            {
                'question': 'Is my data secure?',
                'answer': 'Absolutely. We use bank-level encryption (AES-256) for data at rest and TLS 1.3 for data in transit. We also perform regular security audits and are compliant with industry standards.',
                'order': 8,
            },
            {
                'question': 'Do you provide training and onboarding?',
                'answer': 'Yes! All plans include access to our comprehensive documentation and video tutorials. Professional and Enterprise plans also include personalized onboarding sessions with our team.',
                'order': 9,
            },
            {
                'question': 'Can I get a refund?',
                'answer': 'We offer a 30-day money-back guarantee. If you\'re not satisfied with our service within the first 30 days, contact us for a full refund, no questions asked.',
                'order': 10,
            },
            {
                'question': 'What kind of support do you offer?',
                'answer': 'Support varies by plan: Starter includes email support (24-48 hour response), Professional includes priority email support (12-24 hour response), and Enterprise includes 24/7 phone and email support with a dedicated account manager.',
                'order': 11,
            },
            {
                'question': 'Can I integrate with my existing tools?',
                'answer': 'Yes! Our Professional and Enterprise plans include API access, allowing you to integrate with accounting software, e-commerce platforms, and other business tools. We also offer pre-built integrations for popular services.',
                'order': 12,
            }
        ]
        
        for faq_data in faqs_data:
            faq = FAQ.objects.create(**faq_data)
            self.stdout.write(self.style.SUCCESS(f"[OK] Created FAQ: {faq.question[:50]}..."))
        
        return len(faqs_data)
