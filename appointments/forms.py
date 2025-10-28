from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta
from .models import Appointment
from services.models import Service


class AppointmentBookingForm(forms.ModelForm):
    """Form for booking appointments with vehicle details"""
    
    slot_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date', 
            'min': date.today().strftime('%Y-%m-%d'),
            'class': 'form-control',
            'id': 'id_slot_date'
        }),
        help_text="Select a date for your appointment"
    )
    
    slot_time = forms.ChoiceField(
        choices=[('', 'Select a date first to see available time slots')],
        widget=forms.Select(attrs={
            'class': 'form-control', 
            'id': 'id_slot_time'
        }),
        help_text="Available time slots will be shown based on selected date"
    )
    
    class Meta:
        model = Appointment
        fields = [
            'selected_service', 'slot_date', 'slot_time',
            'vehicle_make', 'vehicle_model', 'vehicle_year', 
            'vehicle_license', 'special_requirements'
        ]
        widgets = {
            'selected_service': forms.Select(attrs={'class': 'form-control'}),
            'vehicle_make': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Toyota'}),
            'vehicle_model': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Camry'}),
            'vehicle_year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1990, 
                'max': timezone.now().year + 1,
                'placeholder': 'e.g., 2020'
            }),
            'vehicle_license': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., ABC-1234'}),
            'special_requirements': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['selected_service'].queryset = Service.objects.filter(is_active=True)
        self.fields['selected_service'].empty_label = "Select a service"
        
        # Populate slot_time with all available choices for validation
        # The new UI handles the display, but form needs all choices for validation
        self.fields['slot_time'].choices = [('', 'Select a time slot')] + list(Appointment.TIME_SLOT_CHOICES)
    
    def clean_slot_date(self):
        selected_date = self.cleaned_data['slot_date']
        if selected_date < date.today():
            raise ValidationError("Cannot book appointments for past dates.")
        if selected_date > date.today() + timedelta(days=30):
            raise ValidationError("Cannot book appointments more than 30 days in advance.")
        return selected_date
    
    def clean(self):
        cleaned_data = super().clean()
        slot_date = cleaned_data.get('slot_date')
        slot_time = cleaned_data.get('slot_time')
        
        if slot_date and slot_time:
            # Check if selected time slot is already occupied
            # Per-slot system: each time slot can only have 1 active appointment
            existing_appointment = Appointment.objects.filter(
                slot_date=slot_date,
                slot_time=slot_time,
                status__in=['booked', 'assigned', 'in_progress', 'on_hold']
            ).first()
            
            if existing_appointment:
                slot_display = dict(Appointment.TIME_SLOT_CHOICES)[slot_time]
                raise ValidationError(
                    f"The {slot_display} time slot is already occupied on {slot_date}. "
                    f"Please select another time slot."
                )
        
        return cleaned_data


class AppointmentSearchForm(forms.Form):
    """Form for searching and filtering appointments"""
    STATUS_CHOICES = [('', 'All Statuses')] + Appointment.STATUS_CHOICES
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by customer, vehicle, or service...'
        })
    )
    status = forms.ChoiceField(
        choices=STATUS_CHOICES, 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
