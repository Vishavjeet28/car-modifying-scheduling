from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Extended User model with role-based access"""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('employee', 'Employee'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    phone_number = models.CharField(max_length=15, blank=True, help_text="Enter phone number in +91XXXXXXXXXX format")
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_customer(self):
        return self.role == 'customer'
    
    def is_employee(self):
        return self.role == 'employee'
    
    def is_admin(self):
        return self.role == 'admin'


class Employee(models.Model):
    """Employee profile model with super employee management capabilities"""
    EMPLOYEE_TYPE_CHOICES = [
        ('regular', 'Regular Employee'),
        ('super', 'Super Employee (Manager)'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('busy', 'Busy'),
        ('break', 'On Break'),
        ('off_duty', 'Off Duty'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    employee_type = models.CharField(max_length=10, choices=EMPLOYEE_TYPE_CHOICES, default='regular')
    specialization = models.CharField(max_length=100, blank=True)
    hire_date = models.DateField()
    is_active = models.BooleanField(default=True)
    current_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    supervisor = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    
    # Performance metrics
    tasks_completed = models.PositiveIntegerField(default=0)
    average_completion_time = models.DurationField(null=True, blank=True)
    performance_rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.0)  # out of 5
    
    # Contact and notes
    phone_extension = models.CharField(max_length=10, blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    notes = models.TextField(blank=True, help_text="Management notes about employee")
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id} ({'Super' if self.is_super_employee() else 'Regular'})"
    
    def is_super_employee(self):
        """Check if this employee is a super employee (manager)"""
        return self.employee_type == 'super'
    
    def can_manage_employees(self):
        """Check if this employee can manage others"""
        return self.is_super_employee() or self.user.is_admin()
    
    def get_subordinates(self):
        """Get all employees under this super employee"""
        if self.is_super_employee():
            return Employee.objects.filter(supervisor=self, is_active=True)
        return Employee.objects.none()
    
    def get_active_assignments(self):
        """Get current active task assignments for this employee"""
        from appointments.models import Appointment
        return Appointment.objects.filter(
            assigned_employee=self.user,
            status__in=['assigned', 'in_progress', 'on_hold']
        ).order_by('slot_date', 'slot_time')
    
    def get_pending_tasks_count(self):
        """Get count of pending tasks"""
        return self.get_active_assignments().count()
    
    def update_performance_metrics(self):
        """Update performance metrics based on completed tasks"""
        from appointments.models import Appointment
        from django.db.models import Avg
        
        completed_tasks = Appointment.objects.filter(
            assigned_employee=self.user,
            status='completed',
            work_started_at__isnull=False,
            work_completed_at__isnull=False
        )
        
        self.tasks_completed = completed_tasks.count()
        
        if completed_tasks.exists():
            avg_duration = completed_tasks.aggregate(
                avg_time=Avg(models.F('work_completed_at') - models.F('work_started_at'))
            )['avg_time']
            self.average_completion_time = avg_duration
        
        self.save()


class TaskAssignment(models.Model):
    """Model to track task assignments from super employees to regular employees"""
    ASSIGNMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    assigned_by = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments_given')
    assigned_to = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='assignments_received')
    appointment = models.ForeignKey('appointments.Appointment', on_delete=models.CASCADE, null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=ASSIGNMENT_STATUS_CHOICES, default='pending')
    
    # Timing
    assigned_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Progress tracking
    progress_percentage = models.PositiveIntegerField(default=0)
    employee_notes = models.TextField(blank=True)
    supervisor_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-assigned_at']
    
    def __str__(self):
        return f"{self.title} - {self.assigned_to.user.get_full_name()} ({self.get_status_display()})"
    
    def is_overdue(self):
        """Check if assignment is overdue"""
        from django.utils import timezone
        return timezone.now() > self.due_date and self.status not in ['completed', 'rejected']
    
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
            'pending': 'warning',
            'accepted': 'info',
            'in_progress': 'primary',
            'completed': 'success',
            'rejected': 'danger'
        }
        return colors.get(self.status, 'secondary')