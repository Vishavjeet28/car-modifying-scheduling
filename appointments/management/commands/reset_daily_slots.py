from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from appointments.models import Appointment


class Command(BaseCommand):
    help = 'Reset appointment slots for the next day (run daily at midnight)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days ahead to ensure slots are available (default: 30)'
        )

    def handle(self, *args, **options):
        days_ahead = options['days']
        
        # This command doesn't need to create slots since our system
        # dynamically calculates availability based on existing bookings
        
        # However, we can clean up old cancelled appointments
        cutoff_date = date.today() - timedelta(days=30)
        old_cancelled = Appointment.objects.filter(
            status='cancelled',
            slot_date__lt=cutoff_date
        )
        
        count = old_cancelled.count()
        old_cancelled.delete()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cleaned up {count} old cancelled appointments'
            )
        )
        
        # Log current slot availability for today
        today = date.today()
        for slot_time, slot_display in Appointment.TIME_SLOT_CHOICES:
            remaining = Appointment.get_slot_capacity(today, slot_time)
            self.stdout.write(
                f'Today {slot_display}: {remaining}/5 slots available'
            )