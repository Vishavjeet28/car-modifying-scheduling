from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import User, Employee
from appointments.models import Appointment


class CustomLoginView(LoginView):
    """Custom login view with role-based redirection"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        user = self.request.user
        if user.is_admin():
            return reverse_lazy('accounts:admin_dashboard')
        elif user.is_employee():
            return reverse_lazy('accounts:employee_dashboard')
        else:
            return reverse_lazy('accounts:dashboard')


def register_view(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # If user registered as employee, create Employee profile
            if user.role == 'employee':
                Employee.objects.create(
                    user=user,
                    employee_id=f"EMP{user.id:04d}",
                    specialization="General",
                    hire_date=timezone.now().date(),
                    is_active=True
                )
                messages.success(request, f'Welcome to CarModX, {user.get_full_name()}! Your employee profile has been created.')
            else:
                messages.success(request, f'Welcome to CarModX, {user.get_full_name()}!')
            
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard_view(request):
    """Customer dashboard view"""
    user = request.user
    
    if user.is_admin():
        return redirect('accounts:admin_dashboard')
    elif user.is_employee():
        return redirect('accounts:employee_dashboard')
    
    # Customer dashboard
    recent_appointments = Appointment.objects.filter(
        customer=user
    ).order_by('-created_at')[:5]
    
    upcoming_appointments = Appointment.objects.filter(
        customer=user,
        status='booked'
    ).order_by('slot_date', 'slot_time')
    
    context = {
        'recent_appointments': recent_appointments,
        'upcoming_appointments': upcoming_appointments,
    }
    
    return render(request, 'accounts/dashboard.html', context)


@login_required
def employee_dashboard_view(request):
    """Employee dashboard view - focused on work management"""
    if not request.user.is_employee() and not request.user.is_staff:
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('accounts:dashboard')
    
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        # If no employee profile exists, create one for staff users
        if request.user.is_staff:
            employee = Employee.objects.create(
                user=request.user,
                employee_id=f"EMP{request.user.id:04d}",
                specialization="General",
                hire_date=timezone.now().date(),
                is_active=True
            )
        else:
            messages.error(request, 'Employee profile not found.')
            return redirect('accounts:dashboard')
    
    from datetime import date, timedelta
    today = date.today()
    
    # Get work assignments for this employee
    my_assigned_work = Appointment.objects.filter(
        assigned_employee=request.user,
        status__in=['assigned', 'in_progress', 'on_hold']
    ).order_by('slot_date', 'slot_time')
    
    # Get today's work (all work scheduled for today)
    today_work = Appointment.objects.filter(
        slot_date=today,
        status__in=['booked', 'assigned', 'in_progress']
    ).order_by('slot_time')
    
    # Get unassigned work that can be picked up
    available_work = Appointment.objects.filter(
        assigned_employee__isnull=True,
        status='booked',
        slot_date__gte=today
    ).order_by('slot_date', 'slot_time')[:10]
    
    # Get upcoming work (next 7 days)
    upcoming_work = Appointment.objects.filter(
        slot_date__gt=today,
        slot_date__lte=today + timedelta(days=7),
        status__in=['booked', 'assigned', 'in_progress']
    ).order_by('slot_date', 'slot_time')
    
    # Get recent completed work by this employee
    completed_work = Appointment.objects.filter(
        assigned_employee=request.user,
        status='completed'
    ).order_by('-work_completed_at')[:5]
    
    # Get work statistics
    my_active_work = Appointment.objects.filter(
        assigned_employee=request.user,
        status__in=['assigned', 'in_progress', 'on_hold']
    ).count()
    
    my_completed_today = Appointment.objects.filter(
        assigned_employee=request.user,
        status='completed',
        work_completed_at__date=today
    ).count()
    
    urgent_work = Appointment.objects.filter(
        priority='urgent',
        status__in=['booked', 'assigned', 'in_progress']
    ).count()
    
    total_available = available_work.count()
    
    context = {
        'employee': employee,
        'my_assigned_work': my_assigned_work,
        'today_work': today_work,
        'available_work': available_work,
        'upcoming_work': upcoming_work,
        'completed_work': completed_work,
        'my_active_work': my_active_work,
        'my_completed_today': my_completed_today,
        'urgent_work': urgent_work,
        'total_available': total_available,
        'today': today,
    }
    
    return render(request, 'accounts/employee_dashboard.html', context)


@login_required
def admin_dashboard_view(request):
    """Admin dashboard view - placeholder for now"""
    if not request.user.is_admin():
        messages.error(request, 'Access denied. Admin access required.')
        return redirect('accounts:dashboard')
    
    # TODO: Implement full admin dashboard in Part 3
    return render(request, 'accounts/admin_dashboard.html', {
        'message': 'Admin Dashboard - Coming in Part 3!'
    })


@login_required
def profile_view(request):
    """User profile view"""
    # TODO: Implement profile form after User model is created
    return render(request, 'accounts/profile.html', {})


@login_required
def appointment_history_view(request):
    """View appointment history for customers"""
    if not request.user.is_customer():
        messages.error(request, 'Access denied.')
        return redirect('accounts:dashboard')
    
    appointments = Appointment.objects.filter(
        customer=request.user
    ).order_by('-created_at')
    
    return render(request, 'accounts/appointment_history.html', {
        'appointments': appointments
    })


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')