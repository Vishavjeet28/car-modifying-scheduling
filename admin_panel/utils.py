"""
Utility functions for admin panel operations
"""
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from .models import AdminLog


def log_admin_action(user, action, request=None, content_object=None, 
                    change_message='', view_kwargs=None):
    """
    Log an admin action for audit trail
    
    Args:
        user: The user performing the action
        action: String describing the action performed
        request: The HTTP request object (optional)
        content_object: The object being acted upon (optional)
        change_message: Description of changes made (optional)
        view_kwargs: View keyword arguments (optional)
    """
    log_entry = AdminLog(
        admin_user=user,
        action=action,
        change_message=change_message,
        timestamp=timezone.now()
    )
    
    # If we have a content object, log its details
    if content_object:
        log_entry.content_type = ContentType.objects.get_for_model(content_object)
        log_entry.object_id = content_object.pk
        log_entry.object_repr = str(content_object)
    
    # Add request information if available
    if request:
        log_entry.ip_address = get_client_ip(request)
        log_entry.user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
    
    # Add view context if available
    if view_kwargs:
        log_entry.extra_data = str(view_kwargs)
    
    log_entry.save()
    return log_entry


def get_client_ip(request):
    """
    Get the client IP address from the request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_admin_statistics():
    """
    Calculate comprehensive admin dashboard statistics with caching
    """
    from django.core.cache import cache
    from django.contrib.auth import get_user_model
    from services.models import Service, ServiceCategory
    from appointments.models import Appointment
    from accounts.models import Employee
    from django.db.models import Count, Sum, Q, Avg
    from datetime import datetime, timedelta
    from decimal import Decimal
    
    # Check cache first
    cache_key = 'admin_dashboard_stats'
    cached_stats = cache.get(cache_key)
    if cached_stats:
        return cached_stats
    
    User = get_user_model()
    now = timezone.now()
    
    # Basic counts
    total_services = Service.objects.count()
    active_services = Service.objects.filter(is_active=True).count()
    total_categories = ServiceCategory.objects.count()
    active_categories = ServiceCategory.objects.filter(is_active=True).count()
    
    # Employee statistics
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(is_active=True).count()
    
    # Appointment statistics
    total_appointments = Appointment.objects.count()
    booked_appointments = Appointment.objects.filter(status='booked').count()
    assigned_appointments = Appointment.objects.filter(status='assigned').count()
    in_progress_appointments = Appointment.objects.filter(status='in_progress').count()
    on_hold_appointments = Appointment.objects.filter(status='on_hold').count()
    completed_appointments = Appointment.objects.filter(status='completed').count()
    cancelled_appointments = Appointment.objects.filter(status='cancelled').count()
    
    # Revenue calculations - using service base_price since final_price doesn't exist
    total_revenue = Appointment.objects.filter(
        status='completed'
    ).aggregate(
        total=Sum('selected_service__base_price')
    )['total'] or Decimal('0.00')
    
    estimated_revenue = Appointment.objects.filter(
        status__in=['booked', 'assigned', 'in_progress']
    ).aggregate(
        total=Sum('selected_service__base_price')
    )['total'] or Decimal('0.00')
    
    # Time-based statistics
    today = now.date()
    this_week_start = today - timedelta(days=today.weekday())
    this_month_start = today.replace(day=1)
    last_30_days = now - timedelta(days=30)
    
    # Today's appointments
    today_appointments = Appointment.objects.filter(
        slot_date=today
    ).count()
    
    # This week's appointments
    week_appointments = Appointment.objects.filter(
        slot_date__gte=this_week_start
    ).count()
    
    # This month's appointments
    month_appointments = Appointment.objects.filter(
        slot_date__gte=this_month_start
    ).count()
    
    # Recent activity (last 30 days)
    recent_appointments = Appointment.objects.filter(
        created_at__gte=last_30_days
    ).count()
    
    recent_revenue = Appointment.objects.filter(
        work_completed_at__gte=last_30_days,
        status='completed'
    ).aggregate(
        total=Sum('selected_service__base_price')
    )['total'] or Decimal('0.00')
    
    # Popular services (top 5 by appointment count)
    popular_services = list(
        Service.objects.annotate(
            appointment_count=Count('appointments')
        ).order_by('-appointment_count')[:5].values(
            'name', 'appointment_count', 'base_price'
        )
    )
    
    # Employee performance (appointments completed in last 30 days)
    # Note: Using User model since Appointment.assigned_employee points to User, not Employee
    employee_performance = []
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        employee_users = User.objects.filter(
            role='employee',
            employee_profile__is_active=True
        ).annotate(
            completed_appointments=Count(
                'assigned_work',
                filter=Q(
                    assigned_work__status='completed',
                    assigned_work__work_completed_at__gte=last_30_days
                )
            ),
            total_revenue=Sum(
                'assigned_work__selected_service__base_price',
                filter=Q(
                    assigned_work__status='completed',
                    assigned_work__work_completed_at__gte=last_30_days
                )
            )
        ).order_by('-completed_appointments')[:5]
        
        employee_performance = []
        for user in employee_users:
            try:
                employee_profile = user.employee_profile
                employee_performance.append({
                    'user__first_name': user.first_name,
                    'user__last_name': user.last_name,
                    'employee_id': employee_profile.employee_id,
                    'completed_appointments': user.completed_appointments,
                    'total_revenue': user.total_revenue or 0
                })
            except:
                continue
    except Exception:
        # Fallback to empty list if there are issues
        employee_performance = []
    
    # Appointment trends (last 7 days)
    appointment_trends = []
    for i in range(7):
        date = today - timedelta(days=i)
        count = Appointment.objects.filter(slot_date=date).count()
        appointment_trends.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    appointment_trends.reverse()  # Show oldest to newest
    
    # Service category distribution
    category_stats = list(
        ServiceCategory.objects.annotate(
            service_count=Count('services'),
            appointment_count=Count('services__appointments')
        ).values('name', 'service_count', 'appointment_count')
    )
    
    # Average appointment value
    avg_appointment_value = Appointment.objects.filter(
        status='completed'
    ).aggregate(
        avg=Avg('selected_service__base_price')
    )['avg'] or Decimal('0.00')
    
    # Compile all statistics
    stats = {
        # Basic counts
        'total_services': total_services,
        'active_services': active_services,
        'total_categories': total_categories,
        'active_categories': active_categories,
        'total_employees': total_employees,
        'active_employees': active_employees,
        
        # Appointment statistics
        'total_appointments': total_appointments,
        'booked_appointments': booked_appointments,
        'assigned_appointments': assigned_appointments,
        'in_progress_appointments': in_progress_appointments,
        'on_hold_appointments': on_hold_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        
        # Revenue statistics
        'total_revenue': float(total_revenue),
        'estimated_revenue': float(estimated_revenue),
        'recent_revenue': float(recent_revenue),
        'avg_appointment_value': float(avg_appointment_value),
        
        # Time-based statistics
        'today_appointments': today_appointments,
        'week_appointments': week_appointments,
        'month_appointments': month_appointments,
        'recent_appointments': recent_appointments,
        
        # Performance data
        'popular_services': popular_services,
        'employee_performance': employee_performance,
        'appointment_trends': appointment_trends,
        'category_stats': category_stats,
        
        # Calculated metrics
        'completion_rate': round(
            (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0, 2
        ),
        'cancellation_rate': round(
            (cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0, 2
        ),
        'revenue_per_appointment': round(
            float(total_revenue / completed_appointments) if completed_appointments > 0 else 0, 2
        ),
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, stats, 300)
    
    return stats


def clear_dashboard_cache():
    """
    Clear the dashboard statistics cache
    """
    from django.core.cache import cache
    cache.delete('admin_dashboard_stats')


def get_context_admin_actions(request, context_object=None):
    """
    Generate context-aware admin actions based on current page and object.
    
    Args:
        request: The HTTP request object
        context_object: Optional object to generate actions for
    
    Returns:
        List of admin action dictionaries
    """
    from django.urls import reverse, NoReverseMatch
    from services.models import Service, ServiceCategory
    from accounts.models import Employee
    
    actions = []
    
    if not (request.user.is_authenticated and request.user.is_superuser):
        return actions
    
    try:
        # Always include dashboard link
        actions.append({
            'name': 'Admin Dashboard',
            'url': reverse('admin_panel:dashboard'),
            'icon': 'fas fa-tachometer-alt',
            'class': 'btn-outline-primary'
        })
        
        # Context-specific actions based on object type
        if context_object:
            if isinstance(context_object, Service):
                actions.extend([
                    {
                        'name': 'Edit Service',
                        'url': reverse('admin_panel:service_update', args=[context_object.pk]),
                        'icon': 'fas fa-edit',
                        'class': 'btn-outline-warning'
                    },
                    {
                        'name': 'Manage Pricing',
                        'url': f"{reverse('admin_panel:pricing_matrix')}?service={context_object.pk}",
                        'icon': 'fas fa-dollar-sign',
                        'class': 'btn-outline-info'
                    },
                    {
                        'name': 'All Services',
                        'url': reverse('admin_panel:service_list'),
                        'icon': 'fas fa-list',
                        'class': 'btn-outline-secondary'
                    }
                ])
            
            elif isinstance(context_object, ServiceCategory):
                actions.extend([
                    {
                        'name': 'Edit Category',
                        'url': reverse('admin_panel:category_update', args=[context_object.pk]),
                        'icon': 'fas fa-edit',
                        'class': 'btn-outline-warning'
                    },
                    {
                        'name': 'All Categories',
                        'url': reverse('admin_panel:category_list'),
                        'icon': 'fas fa-tags',
                        'class': 'btn-outline-secondary'
                    }
                ])
            
            elif isinstance(context_object, Employee):
                actions.extend([
                    {
                        'name': 'Edit Employee',
                        'url': reverse('admin_panel:employee_update', args=[context_object.pk]),
                        'icon': 'fas fa-user-edit',
                        'class': 'btn-outline-warning'
                    },
                    {
                        'name': 'Employee Details',
                        'url': reverse('admin_panel:employee_detail', args=[context_object.pk]),
                        'icon': 'fas fa-user',
                        'class': 'btn-outline-info'
                    },
                    {
                        'name': 'All Employees',
                        'url': reverse('admin_panel:employee_list'),
                        'icon': 'fas fa-users',
                        'class': 'btn-outline-secondary'
                    }
                ])
        
        # URL-based actions when no specific object
        else:
            current_url = request.resolver_match
            if current_url:
                namespace = current_url.namespace
                url_name = current_url.url_name
                
                if namespace == 'services':
                    if url_name == 'service_list':
                        actions.extend([
                            {
                                'name': 'Manage Services',
                                'url': reverse('admin_panel:service_list'),
                                'icon': 'fas fa-cogs',
                                'class': 'btn-outline-primary'
                            },
                            {
                                'name': 'Add Service',
                                'url': reverse('admin_panel:service_create'),
                                'icon': 'fas fa-plus',
                                'class': 'btn-outline-success'
                            },
                            {
                                'name': 'Categories',
                                'url': reverse('admin_panel:category_list'),
                                'icon': 'fas fa-tags',
                                'class': 'btn-outline-info'
                            }
                        ])
                
                elif namespace == 'accounts':
                    if url_name in ['employee_dashboard', 'admin_dashboard']:
                        actions.extend([
                            {
                                'name': 'Manage Employees',
                                'url': reverse('admin_panel:employee_list'),
                                'icon': 'fas fa-users',
                                'class': 'btn-outline-info'
                            },
                            {
                                'name': 'System Settings',
                                'url': reverse('admin_panel:settings_list'),
                                'icon': 'fas fa-cog',
                                'class': 'btn-outline-secondary'
                            }
                        ])
    
    except NoReverseMatch:
        pass
    
    return actions


def generate_admin_breadcrumb(request, custom_items=None):
    """
    Generate breadcrumb navigation for admin panel pages.
    
    Args:
        request: The HTTP request object
        custom_items: List of custom breadcrumb items
    
    Returns:
        List of breadcrumb dictionaries
    """
    from django.urls import reverse
    
    breadcrumbs = [
        {'name': 'Admin', 'url': reverse('admin_panel:dashboard'), 'active': False}
    ]
    
    if custom_items:
        breadcrumbs.extend(custom_items)
    
    # Mark the last item as active
    if breadcrumbs:
        breadcrumbs[-1]['active'] = True
    
    return breadcrumbs