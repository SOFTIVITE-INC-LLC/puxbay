from django.core.management.base import BaseCommand
from billing.models import LegalDocument

class Command(BaseCommand):
    help = 'Populates the platform legal pages (global site)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Populating platform legal pages...')
        
        legal_docs = [
            {
                'title': 'Terms of Service',
                'slug': 'terms-of-service',
                'content': """
                    <h2 class='text-2xl font-bold mb-4'>1. Acceptance of Agreement</h2>
                    <p class='mb-4'>By accessing or using Puxbay (the "Platform"), provided by Softivite Inc. LLC ("Company", "we", "us", or "our"), you agree to be bound by these Terms of Service. If you are entering into this agreement on behalf of a business, you represent that you have the authority to bind such entity to these terms.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>2. Description of Service</h2>
                    <p class='mb-4'>Puxbay is a multi-tenant SaaS Point of Sale (POS) and inventory management platform. We provide tools for processing sales, managing inventory across multiple branches, staff attendance tracking, and business analytics. The specific features available to you depend on your selected subscription plan.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>3. Account Registration & Security</h2>
                    <p class='mb-4'>To use the Platform, you must register for an account. You agree to provide accurate, current, and complete information. You are solely responsible for maintaining the confidentiality of your credentials and for all activities that occur under your account. Multi-factor authentication (2FA) is strongly recommended for all administrative accounts.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>4. Fees, Billing, and Renewals</h2>
                    <p class='mb-4'>Subscription fees are billed in advance based on the billing cycle selected (monthly or annually). All fees are non-refundable except as provided in our Refund Policy. We reserve the right to change our fees upon 30 days' notice. Failure to pay fees may result in the suspension or termination of your access to the Platform.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>5. Service Level & Availability</h2>
                    <p class='mb-4'>We strive to maintain a 99.9% uptime for the Platform, excluding scheduled maintenance. However, we do not guarantee that the service will be uninterrupted or error-free. The POS component includes offline-first functionality to allow for continued operations during local network outages.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>6. Intellectual Property Rights</h2>
                    <p class='mb-4'>The Platform and its original content, features, and functionality are and will remain the exclusive property of Softivite Inc. LLC. You retain all rights to the data you input into the Platform ("Customer Data"). You grant us a limited license to host and process Customer Data solely for the purpose of providing the service to you.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>7. Limitation of Liability</h2>
                    <p class='mb-4'>To the maximum extent permitted by law, Softivite Inc. LLC shall not be liable for any indirect, incidental, special, or consequential damages, including loss of profits, data, or business reputation, arising from your use of the Platform.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>8. Governing Law</h2>
                    <p class='mb-4'>These terms shall be governed by and construed in accordance with the laws of the jurisdiction in which Softivite Inc. LLC is registered, without regard to its conflict of law provisions.</p>
                """
            },
            {
                'title': 'Privacy Policy',
                'slug': 'privacy-policy',
                'content': """
                    <h2 class='text-2xl font-bold mb-4'>1. Information Collection</h2>
                    <p class='mb-4'>We collect personal information that you voluntarily provide to us when you register on the Platform, express an interest in obtaining information about us or our products, or otherwise contact us. This includes: Names, Email Addresses, Phone Numbers, Business Locations, and Billing Information.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>2. How We Use Your Information</h2>
                    <p class='mb-4'>We use personal information collected via our Platform for a variety of business purposes, including: to facilitate account creation and logon, to send administrative information, to fulfill and manage your orders, to protect our services, and to respond to legal requests and prevent harm.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>3. Data Processing & Storage</h2>
                    <p class='mb-4'>We implement multi-tenant isolation to ensure that your business data is segregated from other customers. Sensitive fields, such as API keys and payment secrets, are encrypted at rest using industry-standard AES-256 encryption.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>4. Third-Party Service Providers</h2>
                    <p class='mb-4'>We may share your data with third-party vendors who perform services for us or on our behalf and require access to such information to do that work. Examples include: Payment Processing (Stripe, Paystack) and Email Services (SMTP providers).</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>5. Your Privacy Rights</h2>
                    <p class='mb-4'>Depending on your location, you may have certain rights under applicable data protection laws (such as GDPR or CCPA). These may include the right to request access, rectification, or erasure of your personal data. You can manage your privacy settings and export your data directly from the Security Dashboard.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>6. Data Retention</h2>
                    <p class='mb-4'>We will only keep your personal information for as long as it is necessary for the purposes set out in this privacy policy, unless a longer retention period is required or permitted by law.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>7. Policy Updates</h2>
                    <p class='mb-4'>We may update this privacy policy from time to time. The updated version will be indicated by an updated "Last Updated" date and the updated version will be effective as soon as it is accessible.</p>
                """
            },
            {
                'title': 'Refund Policy',
                'slug': 'refund-policy',
                'content': """
                    <h2 class='text-2xl font-bold mb-4'>1. Subscription Refunds</h2>
                    <p class='mb-4'>We want you to be completely satisfied with Puxbay. We offer a full refund if requested within 7 days of the date of your initial subscription payment. After the first 7 days, no refunds will be issued for the remainder of the current billing cycle.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>2. Cancellation Policy</h2>
                    <p class='mb-4'>You may cancel your subscription at any time via the Billing Dashboard. Upon cancellation, you will continue to have full access to the Platform until the end of your current paid billing period. No further charges will be applied after cancellation.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>3. Exceptional Circumstances</h2>
                    <p class='mb-4'>Refund requests made after the 7-day period may be considered on a case-by-case basis at our sole discretion, particularly in cases of technical failure on our part that prevents you from using the service for an extended period.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>4. Transaction Fees</h2>
                    <p class='mb-4'>Please note that third-party payment processors may retain a small transaction fee upon refunding. We do not have control over these fees and they may be subtracted from your total refund amount.</p>
                """
            },
            {
                'title': 'Cookie Policy',
                'slug': 'cookie-policy',
                'content': """
                    <h2 class='text-2xl font-bold mb-4'>1. What are Cookies?</h2>
                    <p class='mb-4'>Cookies are small data files that are placed on your computer or mobile device when you visit a website. Cookies are widely used by website owners in order to make their websites work, or to work more efficiently, as well as to provide reporting information.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>2. Why We Use Cookies</h2>
                    <p class='mb-4'>We use first-party and third-party cookies for several reasons. Some cookies are required for technical reasons in order for our Platform to operate, and we refer to these as "essential" or "strictly necessary" cookies.</p>
                    
                    <h2 class='text-2xl font-bold mb-4'>3. Categories of Cookies We Use</h2>
                    <ul class='list-disc list-inside mb-4 ml-4'>
                        <li class='mb-2'><strong>Essential Cookies:</strong> Necessary to provide you with services available through our Platform and to use some of its features, such as access to secure areas.</li>
                        <li class='mb-2'><strong>Functional Cookies:</strong> Allow us to remember choices you make when you use the Platform, such as remembering your login details or language preference.</li>
                        <li class='mb-2'><strong>Analytics Cookies:</strong> Help us understand how our Platform is being used, how effective marketing campaigns are, or to help us customize our Platform for you.</li>
                    </ul>
                    
                    <h2 class='text-2xl font-bold mb-4'>4. How Can I Control Cookies?</h2>
                    <p class='mb-4'>You have the right to decide whether to accept or reject cookies. You can set or amend your web browser controls to accept or refuse cookies. If you choose to reject cookies, you may still use our website though your access to some functionality and areas of our Platform may be restricted.</p>
                """
            }
        ]
        
        for doc in legal_docs:
            obj, created = LegalDocument.objects.update_or_create(
                slug=doc['slug'],
                defaults={
                    'title': doc['title'],
                    'content': doc['content'],
                    'is_published': True
                }
            )
            if created:
                self.stdout.write(f"Created: {doc['title']}")
            else:
                self.stdout.write(f"Updated: {doc['title']}")

        self.stdout.write(self.style.SUCCESS('Successfully populated global legal pages.'))
