from main.models import FAQ

def populate_faqs():
    # Clear existing
    FAQ.objects.all().delete()
    print("Cleared existing FAQs.")

    # 1. Payment Methods
    FAQ.objects.create(
        question="What payment methods do you accept?",
        answer="We accept all major credit cards (Visa, Mastercard), debit cards, and Mobile Money through our secure integration with Paystack. Your payment information is handled securely and never stored on our servers.",
        order=1
    )

    # 2. Plan Changes
    FAQ.objects.create(
        question="Can I change my plan later?",
        answer="Yes, absolutely! You can upgrade or downgrade your plan at any time from your dashboard. If you upgrade, the change is immediate and pro-rated. If you downgrade, it takes effect at the end of your current billing cycle.",
        order=2
    )

    # 3. Free Trial
    FAQ.objects.create(
        question="Is there a free trial available?",
        answer="Yes! Our Starter plan comes with a 14-day free trial. You can test out all the features, add products, and process transactions to see if it's the right fit for your business before committing.",
        order=3
    )

    # 4. Security
    FAQ.objects.create(
        question="How secure is my business data?",
        answer="Security is our top priority. We use industry-standard encryption for data in transit and at rest. Our servers are hosted in secure data centers with 24/7 monitoring, and we perform regular backups to ensure your data is never lost.",
        order=4
    )

    # 5. Hardware
    FAQ.objects.create(
        question="Can I use my own hardware?",
        answer="Most likely, yes! Our POS is web-based, so it runs on any device with a browser (PC, Mac, Tablet, iPad). It is compatible with most standard USB barcode scanners and receipt printers.",
        order=5
    )
    print("Populated FAQs.")

populate_faqs()
