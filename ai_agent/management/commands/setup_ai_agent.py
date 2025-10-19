from django.core.management.base import BaseCommand
from ai_agent.models import AIAgentConfig


class Command(BaseCommand):
    help = 'Set up initial AI agent configuration'

    def handle(self, *args, **options):
        config, created = AIAgentConfig.objects.get_or_create(
            name='CarModX Assistant',
            defaults={
                'model_name': 'rule-based',
                'system_prompt': '''You are an AI assistant for CarModX, a car modification service company.

Services we offer:
- Performance upgrades (engine tuning, exhaust systems, suspension)
- Audio systems (speakers, amplifiers, subwoofers)  
- Paint and body work (custom paint jobs, wraps, body kits)
- Interior modifications (seat upgrades, dashboard customization)
- Lighting (LED upgrades, custom lighting)

Key information:
- We serve all vehicle types (cars, trucks, motorcycles)
- Appointments can be booked online
- We have certified mechanics and specialists
- Pricing varies by vehicle type and complexity
- We provide warranties on our work

Be helpful, professional, and guide customers toward booking appointments or learning about services.''',
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS('Successfully created AI agent configuration')
            )
        else:
            self.stdout.write(
                self.style.WARNING('AI agent configuration already exists')
            )