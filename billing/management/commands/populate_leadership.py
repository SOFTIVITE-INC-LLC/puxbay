import os
import requests
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from billing.models import LeadershipMember

class Command(BaseCommand):
    help = 'Populate initial leadership members'

    def handle(self, *args, **options):
        members = [
            {
                'name': 'Alex Morgan',
                'role': 'Co-Founder & CEO',
                'bio': 'Former retail manager turned tech entrepreneur. Alex knows the pain of bad POS systems and set out to fix it.',
                'image_url': 'https://images.unsplash.com/photo-1560250097-0b93528c311a?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'order': 1
            },
            {
                'name': 'Sarah Kim',
                'role': 'Co-Founder & CTO',
                'bio': 'Full-stack wizard with 15 years of experience. Sarah ensures our platform is fast, secure, and always online.',
                'image_url': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'order': 2
            },
            {
                'name': 'David Lee',
                'role': 'Head of Operations',
                'bio': 'David keeps the ship sailing smooth, ensuring our support team delivers happiness to every customer.',
                'image_url': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80',
                'order': 3
            }
        ]

        for m_data in members:
            member, created = LeadershipMember.objects.get_or_create(
                name=m_data['name'],
                defaults={
                    'role': m_data['role'],
                    'bio': m_data['bio'],
                    'order': m_data['order']
                }
            )
            
            if created or not member.image:
                self.stdout.write(f"Downloading image for {member.name}...")
                response = requests.get(m_data['image_url'])
                if response.status_code == 200:
                    file_name = f"{member.name.lower().replace(' ', '_')}.jpg"
                    member.image.save(file_name, ContentFile(response.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f"Successfully created/updated {member.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Failed to download image for {member.name}"))
            else:
                self.stdout.write(f"Member {member.name} already exists with image.")

        self.stdout.write(self.style.SUCCESS('Population complete!'))
