from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time, date
from accounts.models import User
from services.models import Service


class Appointment(models.Model):
    """Enhanced appointment booking model with work management features"""
    STATUS_CHOICES = [
        ('booked', 'Booked'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    # Time slots: 9:00 AM, 11:00 AM, 1:00 PM, 3:00 PM, 5:00 PM
    TIME_SLOT_CHOICES = [
        ('09:00', '9:00 AM'),
        ('11:00', '11:00 AM'),
        ('13:00', '1:00 PM'),
        ('15:00', '3:00 PM'),
        ('17:00', '5:00 PM'),
    ]
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    selected_service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')
    slot_date = models.DateField()
    slot_time = models.CharField(max_length=5, choices=TIME_SLOT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    
    # Work assignment
    assigned_employee = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_work',
        limit_choices_to={'role': 'employee'}
    )
    
    # Vehicle details
    vehicle_make = models.CharField(max_length=50)
    vehicle_model = models.CharField(max_length=50)
    vehicle_year = models.PositiveIntegerField()
    vehicle_license = models.CharField(max_length=20)
    
    # Work tracking
    work_started_at = models.DateTimeField(null=True, blank=True)
    work_completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Notes and requirements
    special_requirements = models.TextField(blank=True)
    work_notes = models.TextField(blank=True, help_text="Employee work progress notes")
    customer_notes = models.TextField(blank=True, help_text="Customer special requests")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        # Allow multiple appointments per customer (no unique constraints)
    
    def __str__(self):
        return f"{self.customer.username} - {self.selected_service.name} - {self.slot_date} {self.get_slot_time_display()}"
    
    def clean(self):
        """Validate appointment constraints"""
        if self.slot_date and self.slot_date < date.today():
            raise ValidationError("Cannot book appointments for past dates.")
        
        # Check if the specific TIME SLOT is already occupied
        # A time slot can only have ONE active appointment at a time
        if self.pk is None and self.slot_time and self.slot_date:  # Only for new appointments
            time_slot_occupied = Appointment.objects.filter(
                slot_date=self.slot_date,
                slot_time=self.slot_time,
                status__in=['booked', 'assigned', 'in_progress', 'on_hold']
            ).exists()
            
            if time_slot_occupied:
                slot_display = dict(self.TIME_SLOT_CHOICES).get(self.slot_time, self.slot_time)
                raise ValidationError(
                    f"The {slot_display} time slot is already occupied for {self.slot_date}. "
                    f"This slot is currently being used by another service and will become "
                    f"available once that service is completed. Please select a different time slot."
                )
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def get_available_slots(cls, selected_date):
        """
        Get available time slots for a given date.
        
        A time slot is available if:
        - No active appointment exists for that time slot
        - Active statuses: booked, assigned, in_progress, on_hold
        - Once an appointment is completed or cancelled, the slot becomes available again
        """
        if selected_date < date.today():
            return []
        
        available_slots = []
        
        for slot_time, slot_display in cls.TIME_SLOT_CHOICES:
            # Check if this specific time slot is occupied by an active appointment
            active_appointment = cls.objects.filter(
                slot_date=selected_date,
                slot_time=slot_time,
                status__in=['booked', 'assigned', 'in_progress', 'on_hold']
            ).first()
            
            # If no active appointment exists, the slot is available
            if not active_appointment:
                available_slots.append({
                    'time': slot_time,
                    'display': slot_display,
                    'available': True,
                    'occupied_by': None
                })
        
        return available_slots
    
    @classmethod
    def get_slot_capacity(cls, selected_date, slot_time=None):
        """
        Get slot availability information.
        Since each time slot can only have 1 active appointment, 
        this returns 1 if available, 0 if occupied.
        """
        if slot_time:
            # Check specific time slot
            occupied = cls.objects.filter(
                slot_date=selected_date,
                slot_time=slot_time,
                status__in=['booked', 'assigned', 'in_progress', 'on_hold']
            ).exists()
            return 0 if occupied else 1
        else:
            # Count available slots for the day
            available_count = 0
            for slot_time, _ in cls.TIME_SLOT_CHOICES:
                occupied = cls.objects.filter(
                    slot_date=selected_date,
                    slot_time=slot_time,
                    status__in=['booked', 'assigned', 'in_progress', 'on_hold']
                ).exists()
                if not occupied:
                    available_count += 1
            return available_count
    
    @classmethod
    def get_daily_slot_details(cls, selected_date):
        """
        Get detailed information about all time slots for a specific date.
        Shows which slots are occupied and which are available.
        """
        # Get all active appointments for the date
        active_appointments = cls.objects.filter(
            slot_date=selected_date,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).select_related('customer', 'selected_service', 'assigned_employee').order_by('slot_time')
        
        # Build slot information
        time_slots_info = []
        occupied_count = 0
        
        for slot_time, slot_display in cls.TIME_SLOT_CHOICES:
            # Find appointment occupying this slot
            appointment = active_appointments.filter(slot_time=slot_time).first()
            
            slot_info = {
                'time': slot_time,
                'display': slot_display,
                'occupied': appointment is not None,
                'appointment': None
            }
            
            if appointment:
                occupied_count += 1
                slot_info['appointment'] = {
                    'id': appointment.id,
                    'customer': appointment.customer.username,
                    'service': appointment.selected_service.name,
                    'status': appointment.get_status_display(),
                    'vehicle': f"{appointment.vehicle_make} {appointment.vehicle_model}",
                    'assigned_to': appointment.assigned_employee.username if appointment.assigned_employee else None
                }
            
            time_slots_info.append(slot_info)
        
        return {
            'total_slots': len(cls.TIME_SLOT_CHOICES),
            'occupied_slots': occupied_count,
            'available_slots': len(cls.TIME_SLOT_CHOICES) - occupied_count,
            'slots': time_slots_info,
            'all_appointments': active_appointments
        }
    
    @classmethod
    def get_slot_details(cls, selected_date, slot_time):
        """Get detailed information about what's occupying a specific slot (legacy method)"""
        appointments = cls.objects.filter(
            slot_date=selected_date,
            slot_time=slot_time,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).select_related('customer', 'selected_service', 'assigned_employee')
        
        daily_appointments = cls.objects.filter(
            slot_date=selected_date,
            status__in=['booked', 'assigned', 'in_progress', 'on_hold']
        ).count()
        
        return {
            'total_capacity': 5,  # Daily capacity
            'occupied': appointments.count(),
            'remaining': 5 - daily_appointments,  # Daily remaining
            'appointments': appointments
        }
    
    def can_be_assigned(self):
        """Check if appointment can be assigned to an employee"""
        return self.status in ['booked'] and not self.assigned_employee
    
    def can_start_work(self):
        """Check if work can be started"""
        return self.status in ['booked', 'assigned'] and self.assigned_employee
    
    def can_complete_work(self):
        """Check if work can be completed"""
        return self.status in ['assigned', 'in_progress'] and self.assigned_employee
    
    def get_work_duration(self):
        """Get actual work duration if completed"""
        if self.work_started_at and self.work_completed_at:
            return self.work_completed_at - self.work_started_at
        return None
    
    def is_overdue(self):
        """Check if work is overdue"""
        if self.estimated_completion and timezone.now() > self.estimated_completion:
            return self.status not in ['completed', 'cancelled']
        return False
    
    def get_priority_color(self):
        """Get Bootstrap color class for priority"""
        colors = {
            'low': 'secondary',
            'normal': 'primary',
            'high': 'warning',
            'urgent': 'danger'
        }
        return colors.get(self.priority, 'primary')
    
    def get_status_color(self):
        """Get Bootstrap color class for status"""
        colors = {
            'booked': 'info',
            'assigned': 'primary',
            'in_progress': 'warning',
            'on_hold': 'secondary',
            'completed': 'success',
            'cancelled': 'danger'
        }
        return colors.get(self.status, 'secondary')