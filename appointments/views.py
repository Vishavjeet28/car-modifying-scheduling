from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import Appointment
from .forms import AppointmentBookingForm, AppointmentSearchForm
from services.models import Service

User = get_user_model()


@login_required
def book_appointment_view(request):
    """Book a new appointment with dropdown slot selection"""
    # Only customers can book appointments
    if not request.user.role == 'customer':
        messages.error(request, 'Only customers can book appointments. Employees should manage existing appointments.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.save()
            
            messages.success(request, f'Appointment booked successfully! Your appointment ID is #{appointment.id}')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        form = AppointmentBookingForm(user=request.user)
    
    context = {
        'form': form,
        'services': Service.objects.filter(is_active=True),
    }
    
    return render(request, 'appointments/book_appointment.html', context)


def get_available_slots_api(request):
    """
    API endpoint to get available time slots for a selected date.
    
    Logic:
    - Each time slot can only have 1 active appointment at a time
    - Active statuses: booked, assigned, in_progress, on_hold
    - Completed/cancelled appointments free up the slot
    """
    selected_date = request.GET.get('date')
    
    if not selected_date:
        return JsonResponse({'error': 'Date parameter is required'}, status=400)
    
    try:
        selected_date = date.fromisoformat(selected_date)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    available_slots = Appointment.get_available_slots(selected_date)
    daily_details = Appointment.get_daily_slot_details(selected_date)
    
    # Format slots for dropdown (only available ones)
    formatted_slots = []
    for slot in available_slots:
        formatted_slots.append({
            'time': slot['time'],
            'display': slot['display'],
            'available': True
        })
    
    # Get detailed info about all slots
    all_slots_info = []
    for slot_info in daily_details['slots']:
        all_slots_info.append({
            'time': slot_info['time'],
            'display': slot_info['display'],
            'occupied': slot_info['occupied'],
            'appointment': slot_info['appointment']
        })
    
    return JsonResponse({
        'slots': formatted_slots,  # Only available slots for the dropdown
        'all_slots': all_slots_info,  # All slots with their status
        'date': selected_date.isoformat(),
        'total_slots': daily_details['total_slots'],
        'occupied_slots': daily_details['occupied_slots'],
        'available_slots': daily_details['available_slots'],
        'capacity_info': f'{daily_details["available_slots"]} out of {daily_details["total_slots"]} time slots available for {selected_date}'
    })


@login_required
def appointment_detail_view(request, appointment_id):
    """View appointment details"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions - customers can only see their own appointments, employees can see all
    if request.user != appointment.customer and not (request.user.is_staff or request.user.role == 'employee'):
        messages.error(request, 'Access denied.')
        return redirect('appointments:my_appointments')
    
    context = {
        'appointment': appointment,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
def my_appointments_view(request):
    """List current user's appointments"""
    appointments = Appointment.objects.filter(customer=request.user).order_by('-slot_date', '-slot_time')
    
    # Pagination
    paginator = Paginator(appointments, 10)
    page_number = request.GET.get('page')
    appointments = paginator.get_page(page_number)
    
    context = {
        'appointments': appointments,
    }
    
    return render(request, 'appointments/my_appointments.html', context)


@login_required
def appointment_list_view(request):
    """List all appointments (for staff and employees)"""
    if not (request.user.is_staff or request.user.role == 'employee'):
        messages.error(request, 'Access denied. Only employees can view all appointments.')
        return redirect('appointments:my_appointments')
    
    appointments = Appointment.objects.all()
    
    # Apply search and filters
    search_form = AppointmentSearchForm(request.GET)
    if search_form.is_valid():
        search = search_form.cleaned_data.get('search')
        status = search_form.cleaned_data.get('status')
        date_from = search_form.cleaned_data.get('date_from')
        date_to = search_form.cleaned_data.get('date_to')
        
        if search:
            appointments = appointments.filter(
                Q(customer__username__icontains=search) |
                Q(customer__first_name__icontains=search) |
                Q(customer__last_name__icontains=search) |
                Q(vehicle_make__icontains=search) |
                Q(vehicle_model__icontains=search) |
                Q(selected_service__name__icontains=search)
            )
        
        if status:
            appointments = appointments.filter(status=status)
        
        if date_from:
            appointments = appointments.filter(slot_date__gte=date_from)
        
        if date_to:
            appointments = appointments.filter(slot_date__lte=date_to)
    
    # Order by date and time
    appointments = appointments.order_by('-slot_date', '-slot_time')
    
    # Pagination
    paginator = Paginator(appointments, 20)
    page_number = request.GET.get('page')
    appointments = paginator.get_page(page_number)
    
    context = {
        'appointments': appointments,
        'search_form': search_form,
    }
    
    return render(request, 'appointments/appointment_list.html', context)


@login_required
def cancel_appointment_view(request, appointment_id):
    """Cancel an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user != appointment.customer and not request.user.is_staff:
        messages.error(request, 'Access denied.')
        return redirect('appointments:my_appointments')
    
    # Check if appointment can be cancelled
    if appointment.status != 'booked':
        messages.error(request, 'This appointment cannot be cancelled.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if appointment.slot_date < date.today():
        messages.error(request, 'Cannot cancel past appointments.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    if request.method == 'POST':
        appointment.status = 'cancelled'
        appointment.save()
        
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    return render(request, 'appointments/cancel_appointment.html', {
        'appointment': appointment
    })


@login_required
def update_appointment_status_view(request, appointment_id):
    """Enhanced work status update with self-assignment and tracking"""
    if not (request.user.is_staff or request.user.role == 'employee'):
        messages.error(request, 'Access denied. Only employees can update work status.')
        return redirect('appointments:my_appointments')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'assign_self':
            # Employee assigns themselves to the work
            if appointment.can_be_assigned():
                appointment.assigned_employee = request.user
                appointment.status = 'assigned'
                appointment.save()
                messages.success(request, f'You have been assigned to work #{appointment.id}')
            else:
                messages.error(request, 'This work cannot be assigned.')
                
        elif action == 'start_work':
            # Start working on the appointment
            if appointment.can_start_work() and appointment.assigned_employee == request.user:
                appointment.status = 'in_progress'
                appointment.work_started_at = timezone.now()
                # Estimate completion based on service duration
                if appointment.selected_service.estimated_duration:
                    appointment.estimated_completion = timezone.now() + appointment.selected_service.estimated_duration
                appointment.save()
                messages.success(request, f'Work started on #{appointment.id}')
            else:
                messages.error(request, 'Cannot start this work.')
                
        elif action == 'complete_work':
            # Complete the work
            if appointment.can_complete_work() and appointment.assigned_employee == request.user:
                appointment.status = 'completed'
                appointment.work_completed_at = timezone.now()
                work_notes = request.POST.get('work_notes', '')
                if work_notes:
                    appointment.work_notes = work_notes
                appointment.save()
                messages.success(request, f'Work #{appointment.id} completed successfully!')
            else:
                messages.error(request, 'Cannot complete this work.')
                
        elif action == 'update_status':
            # Manual status update
            new_status = request.POST.get('status')
            new_priority = request.POST.get('priority')
            work_notes = request.POST.get('work_notes', '')
            
            if new_status in dict(Appointment.STATUS_CHOICES):
                old_status = appointment.status
                appointment.status = new_status
                
                if new_priority in dict(Appointment.PRIORITY_CHOICES):
                    appointment.priority = new_priority
                
                if work_notes:
                    appointment.work_notes = work_notes
                
                # Handle status-specific logic
                if new_status == 'in_progress' and old_status != 'in_progress':
                    appointment.work_started_at = timezone.now()
                elif new_status == 'completed' and old_status != 'completed':
                    appointment.work_completed_at = timezone.now()
                elif new_status == 'on_hold':
                    # Work is paused
                    pass
                
                appointment.save()
                messages.success(request, f'Work status updated to {appointment.get_status_display()}')
            else:
                messages.error(request, 'Invalid status.')
        
        return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    
    # Get available employees for assignment
    available_employees = User.objects.filter(role='employee', is_active=True)
    
    context = {
        'appointment': appointment,
        'status_choices': Appointment.STATUS_CHOICES,
        'priority_choices': Appointment.PRIORITY_CHOICES,
        'available_employees': available_employees,
        'can_assign_self': appointment.can_be_assigned(),
        'can_start_work': appointment.can_start_work() and appointment.assigned_employee == request.user,
        'can_complete_work': appointment.can_complete_work() and appointment.assigned_employee == request.user,
        'is_assigned_to_user': appointment.assigned_employee == request.user,
    }
    
    return render(request, 'appointments/update_status.html', context)


@login_required
def slot_occupancy_view(request):
    """View showing current daily slot occupancy (Admin/Staff only)"""
    if not (request.user.is_staff or request.user.role in ['employee', 'admin']):
        messages.error(request, 'Access denied. Staff access required.')
        return redirect('appointments:my_appointments')
    
    # Get date from query params or default to today
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = date.fromisoformat(selected_date)
        except ValueError:
            selected_date = date.today()
    else:
        selected_date = date.today()
    
    # Get daily slot details
    daily_details = Appointment.get_daily_slot_details(selected_date)
    
    # Prepare slot occupancy information
    slot_occupancy = []
    for slot_time, slot_data in daily_details['time_slots'].items():
        slot_display = slot_data['display']
        appointments = slot_data['appointments']
        
        occupancy_info = {
            'time': slot_time,
            'display': slot_display,
            'occupied': len(appointments) > 0,
            'appointments': appointments
        }
        
        slot_occupancy.append(occupancy_info)
    
    context = {
        'slot_occupancy': slot_occupancy,
        'daily_details': daily_details,
        'selected_date': selected_date,
        'today': date.today(),
    }
    
    return render(request, 'appointments/slot_occupancy.html', context)