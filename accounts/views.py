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
from .models import User, Employee, TaskAssignment
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
    """Enhanced employee dashboard - Super Employee Management System"""
    if not request.user.is_employee() and not request.user.is_staff:
        messages.error(request, 'Access denied. Employee access required.')
        return redirect('accounts:dashboard')
    
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found. Please contact administrator.')
        return redirect('accounts:dashboard')
    
    from datetime import date, timedelta
    from .models import TaskAssignment
    today = date.today()
    
    # Check if this is a super employee (manager)
    is_super_employee = employee.is_super_employee()
    
    if is_super_employee:
        # ===== SUPER EMPLOYEE DASHBOARD =====
        
        # Get all employees under management
        all_employees = Employee.objects.filter(is_active=True).exclude(id=employee.id)
        subordinates = employee.get_subordinates()
        
        # Employee performance metrics
        employee_stats = []
        for emp in all_employees:
            active_tasks = emp.get_pending_tasks_count()
            recent_completed = Appointment.objects.filter(
                assigned_employee=emp.user,
                status='completed',
                work_completed_at__date=today
            ).count()
            
            # Get task assignments for this employee
            pending_assignments = TaskAssignment.objects.filter(
                assigned_to=emp,
                status__in=['pending', 'accepted', 'in_progress']
            ).count()
            
            employee_stats.append({
                'employee': emp,
                'active_tasks': active_tasks,
                'completed_today': recent_completed,
                'pending_assignments': pending_assignments,
                'status_color': 'success' if emp.current_status == 'available' else 'warning' if emp.current_status == 'busy' else 'secondary'
            })
        
        # Unassigned work that needs to be assigned
        unassigned_work = Appointment.objects.filter(
            assigned_employee__isnull=True,
            status='booked',
            slot_date__gte=today
        ).order_by('slot_date', 'slot_time')
        
        # Recent task assignments made by this super employee
        my_assignments = TaskAssignment.objects.filter(
            assigned_by=employee
        ).order_by('-assigned_at')[:10]
        
        # Overall statistics
        total_employees = all_employees.count()
        available_employees = all_employees.filter(current_status='available').count()
        busy_employees = all_employees.filter(current_status='busy').count()
        
        total_active_work = Appointment.objects.filter(
            status__in=['assigned', 'in_progress', 'on_hold']
        ).count()
        
        work_completed_today = Appointment.objects.filter(
            status='completed',
            work_completed_at__date=today
        ).count()
        
        overdue_assignments = TaskAssignment.objects.filter(
            assigned_by=employee,
            due_date__lt=timezone.now(),
            status__in=['pending', 'accepted', 'in_progress']
        ).count()
        
        context = {
            'employee': employee,
            'is_super_employee': True,
            'employee_stats': employee_stats,
            'all_employees': all_employees,
            'subordinates': subordinates,
            'unassigned_work': unassigned_work,
            'my_assignments': my_assignments,
            'total_employees': total_employees,
            'available_employees': available_employees,
            'busy_employees': busy_employees,
            'total_active_work': total_active_work,
            'work_completed_today': work_completed_today,
            'overdue_assignments': overdue_assignments,
            'unassigned_count': unassigned_work.count(),
            'today': today,
        }
    
    else:
        # ===== REGULAR EMPLOYEE DASHBOARD =====
        
        # Get work assignments for this employee
        my_assigned_work = Appointment.objects.filter(
            assigned_employee=request.user,
            status__in=['assigned', 'in_progress', 'on_hold']
        ).order_by('slot_date', 'slot_time')
        
        # Get task assignments from super employee
        my_task_assignments = TaskAssignment.objects.filter(
            assigned_to=employee,
            status__in=['pending', 'accepted', 'in_progress']
        ).order_by('-assigned_at')
        
        # Get today's work
        today_work = Appointment.objects.filter(
            assigned_employee=request.user,
            slot_date=today,
            status__in=['assigned', 'in_progress']
        ).order_by('slot_time')
        
        # Get recent completed work
        completed_work = Appointment.objects.filter(
            assigned_employee=request.user,
            status='completed'
        ).order_by('-work_completed_at')[:5]
        
        # Statistics for regular employee
        my_active_work = my_assigned_work.count()
        my_completed_today = Appointment.objects.filter(
            assigned_employee=request.user,
            status='completed',
            work_completed_at__date=today
        ).count()
        
        pending_task_assignments = my_task_assignments.filter(status='pending').count()
        overdue_tasks = my_task_assignments.filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'accepted', 'in_progress']
        ).count()
        
        # Available work that can be picked up by this employee
        available_work = Appointment.objects.filter(
            assigned_employee__isnull=True,
            status='booked',
            slot_date__gte=today
        ).order_by('slot_date', 'slot_time')
        
        # Upcoming work for this employee (next 7 days)
        from datetime import timedelta
        upcoming_work = Appointment.objects.filter(
            assigned_employee=request.user,
            slot_date__gte=today,
            slot_date__lte=today + timedelta(days=7),
            status__in=['assigned', 'in_progress']
        ).order_by('slot_date', 'slot_time')
        
        context = {
            'employee': employee,
            'is_super_employee': False,
            'my_assigned_work': my_assigned_work,
            'my_task_assignments': my_task_assignments,
            'today_work': today_work,
            'completed_work': completed_work,
            'available_work': available_work,
            'upcoming_work': upcoming_work,
            'my_active_work': my_active_work,
            'my_completed_today': my_completed_today,
            'pending_task_assignments': pending_task_assignments,
            'overdue_tasks': overdue_tasks,
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


@login_required
def assign_task_view(request):
    """Super employee assigns tasks to regular employees"""
    try:
        employee = request.user.employee_profile
        if not employee.can_manage_employees():
            messages.error(request, 'Access denied. Super employee privileges required.')
            return redirect('accounts:employee_dashboard')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        # Handle task assignment form submission
        assigned_to_id = request.POST.get('assigned_to')
        appointment_id = request.POST.get('appointment_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        priority = request.POST.get('priority', 'normal')
        due_date = request.POST.get('due_date')
        
        try:
            assigned_to_employee = Employee.objects.get(id=assigned_to_id)
            
            # Create task assignment
            task_assignment = TaskAssignment.objects.create(
                assigned_by=employee,
                assigned_to=assigned_to_employee,
                appointment_id=appointment_id if appointment_id else None,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date
            )
            
            # If it's an appointment assignment, also update the appointment
            if appointment_id:
                appointment = Appointment.objects.get(id=appointment_id)
                appointment.assigned_employee = assigned_to_employee.user
                appointment.status = 'assigned'
                appointment.save()
            
            messages.success(request, f'Task successfully assigned to {assigned_to_employee.user.get_full_name()}')
            
        except Exception as e:
            messages.error(request, f'Error assigning task: {str(e)}')
        
        return redirect('accounts:employee_dashboard')
    
    # GET request - show assignment form
    available_employees = Employee.objects.filter(is_active=True).exclude(id=employee.id)
    unassigned_appointments = Appointment.objects.filter(
        assigned_employee__isnull=True,
        status='booked'
    ).order_by('slot_date', 'slot_time')
    
    context = {
        'employee': employee,
        'available_employees': available_employees,
        'unassigned_appointments': unassigned_appointments,
    }
    
    return render(request, 'accounts/assign_task.html', context)


@login_required 
def update_employee_status_view(request):
    """Super employee updates status of other employees"""
    try:
        employee = request.user.employee_profile
        if not employee.can_manage_employees():
            messages.error(request, 'Access denied. Super employee privileges required.')
            return redirect('accounts:employee_dashboard')
    except Employee.DoesNotExist:
        messages.error(request, 'Employee profile not found.')
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        try:
            target_employee = Employee.objects.get(id=employee_id)
            target_employee.current_status = new_status
            if notes:
                target_employee.notes = notes
            target_employee.save()
            
            messages.success(request, f'Status updated for {target_employee.user.get_full_name()}')
            
        except Employee.DoesNotExist:
            messages.error(request, 'Employee not found.')
        except Exception as e:
            messages.error(request, f'Error updating status: {str(e)}')
    
    return redirect('accounts:employee_dashboard')


@login_required
def task_assignment_detail_view(request, assignment_id):
    """View and update task assignment details"""
    try:
        assignment = TaskAssignment.objects.get(id=assignment_id)
        employee = request.user.employee_profile
        
        # Check permissions - either the assigned employee or the super employee who assigned it
        if assignment.assigned_to != employee and assignment.assigned_by != employee:
            messages.error(request, 'Access denied.')
            return redirect('accounts:employee_dashboard')
            
    except (TaskAssignment.DoesNotExist, Employee.DoesNotExist):
        messages.error(request, 'Assignment not found.')
        return redirect('accounts:employee_dashboard')
    
    if request.method == 'POST':
        # Handle status updates
        if assignment.assigned_to == employee:
            # Regular employee updating their task
            status = request.POST.get('status')
            progress = request.POST.get('progress', 0)
            notes = request.POST.get('employee_notes', '')
            
            assignment.status = status
            assignment.progress_percentage = min(100, max(0, int(progress)))
            assignment.employee_notes = notes
            
            # Set timestamps based on status
            if status == 'accepted' and not assignment.accepted_at:
                assignment.accepted_at = timezone.now()
            elif status == 'in_progress' and not assignment.started_at:
                assignment.started_at = timezone.now()
            elif status == 'completed' and not assignment.completed_at:
                assignment.completed_at = timezone.now()
                assignment.progress_percentage = 100
            
            assignment.save()
            
            # Update employee performance metrics
            employee.update_performance_metrics()
            
            messages.success(request, 'Task status updated successfully.')
            
        elif assignment.assigned_by == employee:
            # Super employee updating supervisor notes
            supervisor_notes = request.POST.get('supervisor_notes', '')
            assignment.supervisor_notes = supervisor_notes
            assignment.save()
            
            messages.success(request, 'Supervisor notes updated.')
    
    context = {
        'assignment': assignment,
        'is_assignee': assignment.assigned_to == employee,
        'is_supervisor': assignment.assigned_by == employee,
    }
    
    return render(request, 'accounts/task_assignment_detail.html', context)


@login_required
def update_task_status_view(request, assignment_id, status):
    """AJAX view to update task assignment status"""
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.utils.decorators import method_decorator
    
    try:
        employee = request.user.employee_profile
        assignment = TaskAssignment.objects.get(id=assignment_id, assigned_to=employee)
        
        # Validate status
        valid_statuses = ['pending', 'accepted', 'in_progress', 'completed']
        if status not in valid_statuses:
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        
        # Update status
        assignment.status = status
        
        if status == 'accepted':
            assignment.accepted_at = timezone.now()
            messages.success(request, f'Task "{assignment.title}" has been accepted.')
        elif status == 'in_progress':
            assignment.started_at = timezone.now()
            messages.success(request, f'Work started on task "{assignment.title}".')
        elif status == 'completed':
            assignment.completed_at = timezone.now()
            assignment.progress_percentage = 100
            messages.success(request, f'Task "{assignment.title}" has been completed!')
        
        assignment.save()
        
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True, 'message': 'Status updated successfully'})
        else:
            return redirect('accounts:employee_dashboard')
            
    except TaskAssignment.DoesNotExist:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Task not found'})
        else:
            messages.error(request, 'Task not found or not assigned to you.')
            return redirect('accounts:employee_dashboard')
    except Employee.DoesNotExist:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'message': 'Employee profile not found'})
        else:
            messages.error(request, 'Employee profile not found.')
            return redirect('accounts:dashboard')


def logout_view(request):
    """Custom logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')