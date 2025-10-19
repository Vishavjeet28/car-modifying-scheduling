from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta
from .models import AdminLog, SystemSettings
from .utils import log_admin_action, get_admin_statistics, clear_dashboard_cache
from .forms import (ServiceForm, ServiceSearchForm, ServiceBulkActionForm, 
                   CategoryForm, CategorySearchForm, CategoryBulkActionForm,
                   ServicePriceForm, PricingSearchForm, BulkPricingForm, PriceImportForm,
                   EmployeeCreateForm, EmployeeUpdateForm, EmployeeSearchForm, EmployeeBulkActionForm)
from services.models import Service, ServiceCategory, ServicePrice
from accounts.models import User, Employee


class SuperUserRequiredMixin(LoginRequiredMixin):
    """Mixin to ensure only super users can access admin views"""
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_superuser:
            return render(request, 'admin_panel/403.html', {
                'error_message': 'You must be a super user to access this page.'
            }, status=403)
        return super().dispatch(request, *args, **kwargs)


class AdminLogMixin:
    """
    Mixin for automatic admin action logging
    """
    log_action = None  # Override in subclasses
    
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        
        # Log successful actions (2xx status codes)
        if (hasattr(response, 'status_code') and 
            200 <= response.status_code < 300 and 
            self.log_action and 
            request.user.is_authenticated):
            
            log_admin_action(
                user=request.user,
                action=self.log_action,
                request=request,
                content_object=getattr(self, 'object', None),
                view_kwargs=kwargs
            )
        
        return response


class AjaxResponseMixin:
    """
    Mixin to handle AJAX requests and responses
    """
    
    def dispatch(self, request, *args, **kwargs):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            try:
                response = super().dispatch(request, *args, **kwargs)
                if hasattr(response, 'status_code') and response.status_code >= 400:
                    return JsonResponse({
                        'success': False,
                        'error': 'An error occurred processing your request.'
                    }, status=response.status_code)
                return response
            except Exception as e:
                return JsonResponse({
                    'success': False,
                    'error': str(e)
                }, status=500)
        return super().dispatch(request, *args, **kwargs)


class AdminDashboardView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """Admin dashboard view with comprehensive statistics and analytics"""
    template_name = 'admin_panel/dashboard.html'
    log_action = 'Viewed Admin Dashboard'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Admin Dashboard'
        context['stats'] = get_admin_statistics()
        
        # Add additional context for dashboard
        from datetime import datetime
        context['current_time'] = datetime.now()
        context['dashboard_refresh_interval'] = 300000  # 5 minutes in milliseconds
        
        return context


class AdminLogListView(SuperUserRequiredMixin, ListView):
    """View for displaying admin action logs"""
    model = AdminLog
    template_name = 'admin_panel/logs/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Admin Logs'
        return context
    
    def get_queryset(self):
        queryset = AdminLog.objects.select_related('admin_user', 'content_type')
        
        # Filter by user if specified
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(admin_user__username__icontains=user_filter)
        
        # Filter by action if specified
        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action__icontains=action_filter)
        
        # Filter by date range if specified
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        
        return queryset


class DashboardStatsAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for refreshing dashboard statistics"""
    
    def get(self, request, *args, **kwargs):
        """Return fresh dashboard statistics as JSON"""
        try:
            # Clear cache to get fresh data
            clear_dashboard_cache()
            stats = get_admin_statistics()
            
            return JsonResponse({
                'success': True,
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Service Management Views

class ServiceListView(SuperUserRequiredMixin, AdminLogMixin, ListView):
    """List view for services with search, filtering, and pagination"""
    model = Service
    template_name = 'admin_panel/services/service_list.html'
    context_object_name = 'services'
    paginate_by = 20
    log_action = 'Viewed Service List'
    
    def get_queryset(self):
        """Filter services based on search and filter parameters"""
        queryset = Service.objects.select_related('category').prefetch_related('prices')
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '').strip()
        category_id = self.request.GET.get('category', '').strip()
        status = self.request.GET.get('status', '').strip()
        price_min = self.request.GET.get('price_min', '').strip()
        price_max = self.request.GET.get('price_max', '').strip()
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )
        
        # Apply category filter
        if category_id:
            try:
                queryset = queryset.filter(category_id=int(category_id))
            except ValueError:
                pass
        
        # Apply status filter
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Apply price range filters
        if price_min:
            try:
                queryset = queryset.filter(base_price__gte=float(price_min))
            except ValueError:
                pass
        
        if price_max:
            try:
                queryset = queryset.filter(base_price__lte=float(price_max))
            except ValueError:
                pass
        
        return queryset.order_by('category__name', 'name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Service Management'
        context['search_form'] = ServiceSearchForm(self.request.GET)
        context['bulk_form'] = ServiceBulkActionForm()
        
        # Add statistics
        context['total_services'] = Service.objects.count()
        context['active_services'] = Service.objects.filter(is_active=True).count()
        context['inactive_services'] = Service.objects.filter(is_active=False).count()
        
        return context


class ServiceCreateView(SuperUserRequiredMixin, AdminLogMixin, CreateView):
    """Create view for services"""
    model = Service
    form_class = ServiceForm
    template_name = 'admin_panel/services/service_form.html'
    success_url = reverse_lazy('admin_panel:service_list')
    log_action = 'Created Service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Service'
        context['form_action'] = 'Create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Service "{form.instance.name}" created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ServiceUpdateView(SuperUserRequiredMixin, AdminLogMixin, UpdateView):
    """Update view for services"""
    model = Service
    form_class = ServiceForm
    template_name = 'admin_panel/services/service_form.html'
    success_url = reverse_lazy('admin_panel:service_list')
    log_action = 'Updated Service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Service: {self.object.name}'
        context['form_action'] = 'Update'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Service "{form.instance.name}" updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class ServiceDeleteView(SuperUserRequiredMixin, AdminLogMixin, DeleteView):
    """Delete view for services"""
    model = Service
    template_name = 'admin_panel/services/service_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:service_list')
    log_action = 'Deleted Service'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Service: {self.object.name}'
        
        # Check for related appointments
        from appointments.models import Appointment
        context['related_appointments'] = Appointment.objects.filter(
            service=self.object
        ).count()
        
        return context
    
    def delete(self, request, *args, **kwargs):
        service_name = self.get_object().name
        messages.success(request, f'Service "{service_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ServiceBulkActionView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle bulk actions on services"""
    log_action = 'Performed Bulk Service Action'
    
    def post(self, request, *args, **kwargs):
        form = ServiceBulkActionForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            service_ids = form.cleaned_data['selected_services']
            new_category = form.cleaned_data.get('new_category')
            
            services = Service.objects.filter(id__in=service_ids)
            count = services.count()
            
            if action == 'activate':
                services.update(is_active=True)
                messages.success(request, f'{count} service(s) activated successfully.')
                
            elif action == 'deactivate':
                services.update(is_active=False)
                messages.success(request, f'{count} service(s) deactivated successfully.')
                
            elif action == 'delete':
                # Check for related appointments before deletion
                from appointments.models import Appointment
                services_with_appointments = []
                for service in services:
                    if Appointment.objects.filter(service=service).exists():
                        services_with_appointments.append(service.name)
                
                if services_with_appointments:
                    messages.error(
                        request, 
                        f'Cannot delete services with existing appointments: {", ".join(services_with_appointments)}'
                    )
                else:
                    service_names = [s.name for s in services]
                    services.delete()
                    messages.success(request, f'Deleted services: {", ".join(service_names)}')
                    
            elif action == 'change_category' and new_category:
                services.update(category=new_category)
                messages.success(
                    request, 
                    f'{count} service(s) moved to category "{new_category.name}" successfully.'
                )
        else:
            messages.error(request, 'Invalid bulk action request.')
        
        return redirect('admin_panel:service_list')


class ServiceDetailAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for service details"""
    
    def get(self, request, pk, *args, **kwargs):
        """Return service details as JSON"""
        try:
            service = get_object_or_404(Service, pk=pk)
            
            # Get service pricing information
            prices = []
            for price in service.prices.filter(is_active=True):
                prices.append({
                    'id': price.id,
                    'vehicle_type': price.vehicle_type,
                    'complexity_level': price.complexity_level,
                    'price': str(price.price)
                })
            
            # Get appointment count
            from appointments.models import Appointment
            appointment_count = Appointment.objects.filter(service=service).count()
            
            data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category.name,
                'base_price': str(service.base_price),
                'estimated_duration': str(service.estimated_duration),
                'is_active': service.is_active,
                'image_url': service.image.url if service.image else None,
                'prices': prices,
                'appointment_count': appointment_count,
                'created_at': service.created_at.isoformat(),
                'updated_at': service.updated_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'service': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Category Management Views

class CategoryListView(SuperUserRequiredMixin, AdminLogMixin, ListView):
    """List view for service categories with search, filtering, and pagination"""
    model = ServiceCategory
    template_name = 'admin_panel/categories/category_list.html'
    context_object_name = 'categories'
    paginate_by = 20
    log_action = 'Viewed Category List'
    
    def get_queryset(self):
        """Filter categories based on search and filter parameters"""
        queryset = ServiceCategory.objects.annotate(
            service_count=Count('services')
        )
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Apply status filter
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Category Management'
        context['search_form'] = CategorySearchForm(self.request.GET)
        context['bulk_form'] = CategoryBulkActionForm()
        
        # Add statistics
        context['total_categories'] = ServiceCategory.objects.count()
        context['active_categories'] = ServiceCategory.objects.filter(is_active=True).count()
        context['inactive_categories'] = ServiceCategory.objects.filter(is_active=False).count()
        
        return context


class CategoryCreateView(SuperUserRequiredMixin, AdminLogMixin, CreateView):
    """Create view for service categories"""
    model = ServiceCategory
    form_class = CategoryForm
    template_name = 'admin_panel/categories/category_form.html'
    success_url = reverse_lazy('admin_panel:category_list')
    log_action = 'Created Category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Category'
        context['form_action'] = 'Create'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class CategoryUpdateView(SuperUserRequiredMixin, AdminLogMixin, UpdateView):
    """Update view for service categories"""
    model = ServiceCategory
    form_class = CategoryForm
    template_name = 'admin_panel/categories/category_form.html'
    success_url = reverse_lazy('admin_panel:category_list')
    log_action = 'Updated Category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Category: {self.object.name}'
        context['form_action'] = 'Update'
        
        # Add service impact warning
        context['service_count'] = self.object.services.count()
        context['active_service_count'] = self.object.services.filter(is_active=True).count()
        
        return context
    
    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class CategoryDeleteView(SuperUserRequiredMixin, AdminLogMixin, DeleteView):
    """Delete view for service categories with dependency checking"""
    model = ServiceCategory
    template_name = 'admin_panel/categories/category_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:category_list')
    log_action = 'Deleted Category'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Category: {self.object.name}'
        
        # Check for related services
        context['related_services'] = self.object.services.all()
        context['service_count'] = self.object.services.count()
        context['active_service_count'] = self.object.services.filter(is_active=True).count()
        
        # Check for related appointments through services
        from appointments.models import Appointment
        context['related_appointments'] = Appointment.objects.filter(
            service__category=self.object
        ).count()
        
        return context
    
    def delete(self, request, *args, **kwargs):
        category = self.get_object()
        
        # Check if category has services
        if category.services.exists():
            messages.error(
                request, 
                f'Cannot delete category "{category.name}" because it has {category.services.count()} associated service(s). '
                'Please move or delete the services first.'
            )
            return redirect('admin_panel:category_list')
        
        category_name = category.name
        messages.success(request, f'Category "{category_name}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


class CategoryBulkActionView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle bulk actions on categories"""
    log_action = 'Performed Bulk Category Action'
    
    def post(self, request, *args, **kwargs):
        form = CategoryBulkActionForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            category_ids = form.cleaned_data['selected_categories']
            
            categories = ServiceCategory.objects.filter(id__in=category_ids)
            count = categories.count()
            
            if action == 'activate':
                categories.update(is_active=True)
                messages.success(request, f'{count} category(ies) activated successfully.')
                
            elif action == 'deactivate':
                categories.update(is_active=False)
                messages.success(request, f'{count} category(ies) deactivated successfully.')
                
            elif action == 'delete':
                # Check for related services before deletion
                categories_with_services = []
                for category in categories:
                    if category.services.exists():
                        categories_with_services.append(f"{category.name} ({category.services.count()} services)")
                
                if categories_with_services:
                    messages.error(
                        request, 
                        f'Cannot delete categories with services: {", ".join(categories_with_services)}'
                    )
                else:
                    category_names = [c.name for c in categories]
                    categories.delete()
                    messages.success(request, f'Deleted categories: {", ".join(category_names)}')
        else:
            messages.error(request, 'Invalid bulk action request.')
        
        return redirect('admin_panel:category_list')


class CategoryDetailAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for category details"""
    
    def get(self, request, pk, *args, **kwargs):
        """Return category details as JSON"""
        try:
            category = get_object_or_404(ServiceCategory, pk=pk)
            
            # Get category services
            services = []
            for service in category.services.all()[:10]:  # Limit to 10 for performance
                services.append({
                    'id': service.id,
                    'name': service.name,
                    'base_price': str(service.base_price),
                    'is_active': service.is_active
                })
            
            # Get appointment count through services
            from appointments.models import Appointment
            appointment_count = Appointment.objects.filter(service__category=category).count()
            
            data = {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'icon': category.icon,
                'is_active': category.is_active,
                'service_count': category.services.count(),
                'active_service_count': category.services.filter(is_active=True).count(),
                'services': services,
                'appointment_count': appointment_count,
                'created_at': category.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'category': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# Pricing Management Views

class ServicePricingView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """Main view for managing service pricing with matrix display"""
    template_name = 'admin_panel/pricing/pricing_matrix.html'
    log_action = 'Viewed Pricing Matrix'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Pricing Management'
        
        # Get service if specified
        service_id = self.request.GET.get('service')
        if service_id:
            try:
                context['selected_service'] = get_object_or_404(Service, pk=int(service_id))
            except (ValueError, Service.DoesNotExist):
                context['selected_service'] = None
        
        # Get all services for dropdown
        context['services'] = Service.objects.filter(is_active=True).select_related('category')
        
        # Get distinct vehicle types and complexity levels for matrix
        context['vehicle_types'] = ServicePrice.objects.values_list('vehicle_type', flat=True).distinct().order_by('vehicle_type')
        context['complexity_levels'] = ServicePrice.objects.values_list('complexity_level', flat=True).distinct().order_by('complexity_level')
        
        # Get pricing data for matrix
        if 'selected_service' in context and context['selected_service']:
            service = context['selected_service']
            prices = ServicePrice.objects.filter(service=service)
            
            # Create pricing matrix with all prices (active and inactive)
            pricing_matrix = {}
            for price in prices:
                key = f"{price.vehicle_type},{price.complexity_level}"
                pricing_matrix[key] = {
                    'id': price.id,
                    'price': price.price,
                    'is_active': price.is_active
                }
            context['pricing_matrix'] = pricing_matrix
        
        # Statistics
        context['total_prices'] = ServicePrice.objects.count()
        context['active_prices'] = ServicePrice.objects.filter(is_active=True).count()
        context['services_with_pricing'] = Service.objects.filter(prices__isnull=False).distinct().count()
        
        return context


class PriceCreateView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Create new service price"""
    log_action = 'Created Service Price'
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX price creation"""
        try:
            service_id = request.POST.get('service_id')
            vehicle_type = request.POST.get('vehicle_type', '').strip()
            complexity_level = request.POST.get('complexity_level', '').strip()
            price = request.POST.get('price')
            
            # Validation
            if not all([service_id, vehicle_type, complexity_level, price]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required.'
                }, status=400)
            
            try:
                service = Service.objects.get(pk=int(service_id))
                price_value = float(price)
                
                if price_value <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Price must be greater than 0.'
                    }, status=400)
                
            except (ValueError, Service.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid service or price value.'
                }, status=400)
            
            # Check for existing price with same combination
            existing = ServicePrice.objects.filter(
                service=service,
                vehicle_type=vehicle_type,
                complexity_level=complexity_level
            ).first()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': f'Price already exists for {vehicle_type} - {complexity_level}. Use update instead.'
                }, status=400)
            
            # Create new price
            service_price = ServicePrice.objects.create(
                service=service,
                vehicle_type=vehicle_type,
                complexity_level=complexity_level,
                price=price_value,
                is_active=True
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Price created successfully for {vehicle_type} - {complexity_level}.',
                'price': {
                    'id': service_price.id,
                    'vehicle_type': service_price.vehicle_type,
                    'complexity_level': service_price.complexity_level,
                    'price': str(service_price.price),
                    'is_active': service_price.is_active
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


class PriceUpdateView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Update existing service price"""
    log_action = 'Updated Service Price'
    
    def post(self, request, pk, *args, **kwargs):
        """Handle AJAX price update"""
        try:
            service_price = get_object_or_404(ServicePrice, pk=pk)
            
            # Get updated values
            vehicle_type = request.POST.get('vehicle_type', '').strip()
            complexity_level = request.POST.get('complexity_level', '').strip()
            price = request.POST.get('price')
            is_active = request.POST.get('is_active') == 'true'
            
            # Validation
            if not all([vehicle_type, complexity_level, price]):
                return JsonResponse({
                    'success': False,
                    'error': 'All fields are required.'
                }, status=400)
            
            try:
                price_value = float(price)
                if price_value <= 0:
                    return JsonResponse({
                        'success': False,
                        'error': 'Price must be greater than 0.'
                    }, status=400)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid price value.'
                }, status=400)
            
            # Check for conflicts (same service, vehicle_type, complexity_level)
            existing = ServicePrice.objects.filter(
                service=service_price.service,
                vehicle_type=vehicle_type,
                complexity_level=complexity_level
            ).exclude(pk=service_price.pk).first()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'error': f'Another price already exists for {vehicle_type} - {complexity_level}.'
                }, status=400)
            
            # Check if price is used in active appointments
            from appointments.models import Appointment
            active_appointments = Appointment.objects.filter(
                service=service_price.service,
                status__in=['pending', 'confirmed', 'in_progress']
            ).count()
            
            if active_appointments > 0 and not is_active:
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot deactivate price. {active_appointments} active appointment(s) use this service.'
                }, status=400)
            
            # Update price
            service_price.vehicle_type = vehicle_type
            service_price.complexity_level = complexity_level
            service_price.price = price_value
            service_price.is_active = is_active
            service_price.save()
            
            return JsonResponse({
                'success': True,
                'message': f'Price updated successfully for {vehicle_type} - {complexity_level}.',
                'price': {
                    'id': service_price.id,
                    'vehicle_type': service_price.vehicle_type,
                    'complexity_level': service_price.complexity_level,
                    'price': str(service_price.price),
                    'is_active': service_price.is_active
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


class PriceDeleteView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Delete service price"""
    log_action = 'Deleted Service Price'
    
    def post(self, request, pk, *args, **kwargs):
        """Handle AJAX price deletion"""
        try:
            service_price = get_object_or_404(ServicePrice, pk=pk)
            
            # Check if price is used in active appointments
            from appointments.models import Appointment
            active_appointments = Appointment.objects.filter(
                service=service_price.service,
                status__in=['pending', 'confirmed', 'in_progress']
            )
            
            if active_appointments.exists():
                appointment_count = active_appointments.count()
                return JsonResponse({
                    'success': False,
                    'error': f'Cannot delete price. {appointment_count} active appointment(s) use this service.'
                }, status=400)
            
            # Store info for response
            vehicle_type = service_price.vehicle_type
            complexity_level = service_price.complexity_level
            
            # Delete price
            service_price.delete()
            
            return JsonResponse({
                'success': True,
                'message': f'Price deleted successfully for {vehicle_type} - {complexity_level}.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


class PricingConflictCheckView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """Check for pricing conflicts before creating/updating"""
    
    def post(self, request, *args, **kwargs):
        """Check for pricing conflicts"""
        try:
            service_id = request.POST.get('service_id')
            vehicle_type = request.POST.get('vehicle_type', '').strip()
            complexity_level = request.POST.get('complexity_level', '').strip()
            exclude_id = request.POST.get('exclude_id')  # For updates
            
            if not all([service_id, vehicle_type, complexity_level]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required fields.'
                }, status=400)
            
            try:
                service = Service.objects.get(pk=int(service_id))
            except (ValueError, Service.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid service.'
                }, status=400)
            
            # Check for existing price
            existing_query = ServicePrice.objects.filter(
                service=service,
                vehicle_type=vehicle_type,
                complexity_level=complexity_level
            )
            
            if exclude_id:
                try:
                    existing_query = existing_query.exclude(pk=int(exclude_id))
                except ValueError:
                    pass
            
            existing = existing_query.first()
            
            if existing:
                return JsonResponse({
                    'success': False,
                    'conflict': True,
                    'message': f'Price already exists for {vehicle_type} - {complexity_level}.',
                    'existing_price': {
                        'id': existing.id,
                        'price': str(existing.price),
                        'is_active': existing.is_active
                    }
                })
            
            return JsonResponse({
                'success': True,
                'conflict': False,
                'message': 'No conflicts found.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


class ServicePricesAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """Get all prices for a specific service"""
    
    def get(self, request, service_id, *args, **kwargs):
        """Return service prices as JSON"""
        try:
            service = get_object_or_404(Service, pk=service_id)
            
            prices = []
            for price in service.prices.all().order_by('vehicle_type', 'complexity_level'):
                prices.append({
                    'id': price.id,
                    'vehicle_type': price.vehicle_type,
                    'complexity_level': price.complexity_level,
                    'price': str(price.price),
                    'is_active': price.is_active
                })
            
            return JsonResponse({
                'success': True,
                'service': {
                    'id': service.id,
                    'name': service.name,
                    'base_price': str(service.base_price)
                },
                'prices': prices
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class BulkPricingUpdateView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle bulk pricing operations"""
    log_action = 'Performed Bulk Pricing Update'
    
    def post(self, request, *args, **kwargs):
        """Handle bulk pricing updates"""
        try:
            action = request.POST.get('action')
            service_id = request.POST.get('service_id')
            
            if not all([action, service_id]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters.'
                }, status=400)
            
            try:
                service = Service.objects.get(pk=int(service_id))
            except (ValueError, Service.DoesNotExist):
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid service.'
                }, status=400)
            
            if action == 'activate_all':
                updated = service.prices.update(is_active=True)
                return JsonResponse({
                    'success': True,
                    'message': f'Activated {updated} price(s) for {service.name}.'
                })
                
            elif action == 'deactivate_all':
                # Check for active appointments
                from appointments.models import Appointment
                active_appointments = Appointment.objects.filter(
                    service=service,
                    status__in=['pending', 'confirmed', 'in_progress']
                ).count()
                
                if active_appointments > 0:
                    return JsonResponse({
                        'success': False,
                        'error': f'Cannot deactivate prices. {active_appointments} active appointment(s) use this service.'
                    }, status=400)
                
                updated = service.prices.update(is_active=False)
                return JsonResponse({
                    'success': True,
                    'message': f'Deactivated {updated} price(s) for {service.name}.'
                })
                
            elif action == 'delete_all':
                # Check for active appointments
                from appointments.models import Appointment
                active_appointments = Appointment.objects.filter(
                    service=service,
                    status__in=['pending', 'confirmed', 'in_progress']
                ).count()
                
                if active_appointments > 0:
                    return JsonResponse({
                        'success': False,
                        'error': f'Cannot delete prices. {active_appointments} active appointment(s) use this service.'
                    }, status=400)
                
                deleted_count = service.prices.count()
                service.prices.all().delete()
                return JsonResponse({
                    'success': True,
                    'message': f'Deleted {deleted_count} price(s) for {service.name}.'
                })
                
            elif action == 'apply_percentage':
                percentage = request.POST.get('percentage')
                try:
                    percentage_value = float(percentage)
                except (ValueError, TypeError):
                    return JsonResponse({
                        'success': False,
                        'error': 'Invalid percentage value.'
                    }, status=400)
                
                updated_count = 0
                for price in service.prices.all():
                    new_price = price.price * (1 + percentage_value / 100)
                    if new_price > 0:
                        price.price = round(new_price, 2)
                        price.save()
                        updated_count += 1
                
                return JsonResponse({
                    'success': True,
                    'message': f'Applied {percentage}% change to {updated_count} price(s) for {service.name}.'
                })
            
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid action.'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': f'An error occurred: {str(e)}'
            }, status=500)


# Employee Management Views

class EmployeeListView(SuperUserRequiredMixin, AdminLogMixin, ListView):
    """List view for employees with search, filtering, and pagination"""
    model = Employee
    template_name = 'admin_panel/employees/employee_list.html'
    context_object_name = 'employees'
    paginate_by = 20
    log_action = 'Viewed Employee List'
    
    def get_queryset(self):
        """Filter employees based on search and filter parameters"""
        queryset = Employee.objects.select_related('user').annotate(
            completed_appointments_count=Count('user__assigned_work', filter=Q(user__assigned_work__status='completed'))
        )
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '').strip()
        status = self.request.GET.get('status', '').strip()
        specialization = self.request.GET.get('specialization', '').strip()
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_query) |
                Q(user__last_name__icontains=search_query) |
                Q(user__username__icontains=search_query) |
                Q(user__email__icontains=search_query) |
                Q(employee_id__icontains=search_query) |
                Q(specialization__icontains=search_query)
            )
        
        # Apply status filter
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Apply specialization filter
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        return queryset.order_by('user__first_name', 'user__last_name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Employee Management'
        context['search_form'] = EmployeeSearchForm(self.request.GET)
        context['bulk_form'] = EmployeeBulkActionForm()
        
        # Add statistics
        context['total_employees'] = Employee.objects.count()
        context['active_employees'] = Employee.objects.filter(is_active=True).count()
        context['inactive_employees'] = Employee.objects.filter(is_active=False).count()
        
        # Get distinct specializations for filter
        context['specializations'] = Employee.objects.values_list('specialization', flat=True).distinct().exclude(specialization='')
        
        return context


class EmployeeCreateView(SuperUserRequiredMixin, AdminLogMixin, CreateView):
    """Create view for employees that creates both User and Employee records"""
    model = Employee
    form_class = EmployeeCreateForm
    template_name = 'admin_panel/employees/employee_form.html'
    success_url = reverse_lazy('admin_panel:employee_list')
    log_action = 'Created Employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create Employee'
        context['form_action'] = 'Create'
        return context
    
    def form_valid(self, form):
        try:
            # Create User first
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data['password'],
                role='employee',
                phone_number=form.cleaned_data.get('phone_number', ''),
                address=form.cleaned_data.get('address', '')
            )
            
            # Create Employee profile
            form.instance.user = user
            
            messages.success(
                self.request, 
                f'Employee "{user.get_full_name()}" (ID: {form.instance.employee_id}) created successfully.'
            )
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error creating employee: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class EmployeeUpdateView(SuperUserRequiredMixin, AdminLogMixin, UpdateView):
    """Update view for employees - updates both User and Employee records"""
    model = Employee
    form_class = EmployeeUpdateForm
    template_name = 'admin_panel/employees/employee_form.html'
    success_url = reverse_lazy('admin_panel:employee_list')
    log_action = 'Updated Employee'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Employee: {self.object.user.get_full_name()}'
        context['form_action'] = 'Update'
        context['employee'] = self.object
        return context
    
    def get_initial(self):
        """Pre-populate form with user data"""
        initial = super().get_initial()
        user = self.object.user
        initial.update({
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'address': user.address,
        })
        return initial
    
    def form_valid(self, form):
        try:
            # Update User record
            user = self.object.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.phone_number = form.cleaned_data.get('phone_number', '')
            user.address = form.cleaned_data.get('address', '')
            
            # Update password if provided
            new_password = form.cleaned_data.get('password')
            if new_password:
                user.set_password(new_password)
            
            user.save()
            
            messages.success(
                self.request, 
                f'Employee "{user.get_full_name()}" updated successfully.'
            )
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error updating employee: {str(e)}')
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class EmployeeDetailView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """Detail view for employees with appointment history and performance tracking"""
    template_name = 'admin_panel/employees/employee_detail.html'
    log_action = 'Viewed Employee Detail'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get employee
        employee_id = kwargs.get('pk')
        employee = get_object_or_404(Employee.objects.select_related('user'), pk=employee_id)
        context['employee'] = employee
        context['page_title'] = f'Employee Details: {employee.user.get_full_name()}'
        
        # Get appointment history
        from appointments.models import Appointment
        appointments = Appointment.objects.filter(employee=employee).select_related(
            'customer', 'service', 'time_slot'
        ).order_by('-created_at')
        
        # Paginate appointments
        paginator = Paginator(appointments, 10)
        page_number = self.request.GET.get('page')
        context['appointments'] = paginator.get_page(page_number)
        
        # Calculate performance metrics
        total_appointments = appointments.count()
        completed_appointments = appointments.filter(status='completed').count()
        cancelled_appointments = appointments.filter(status='cancelled').count()
        pending_appointments = appointments.filter(status__in=['pending', 'confirmed']).count()
        
        context['performance_stats'] = {
            'total_appointments': total_appointments,
            'completed_appointments': completed_appointments,
            'cancelled_appointments': cancelled_appointments,
            'pending_appointments': pending_appointments,
            'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
            'cancellation_rate': (cancelled_appointments / total_appointments * 100) if total_appointments > 0 else 0,
        }
        
        # Get recent appointments (last 30 days)
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_appointments = appointments.filter(created_at__gte=thirty_days_ago)
        context['recent_appointments_count'] = recent_appointments.count()
        
        # Get appointment status distribution for charts
        status_distribution = {}
        for status, _ in Appointment.STATUS_CHOICES:
            count = appointments.filter(status=status).count()
            if count > 0:
                status_distribution[status.title()] = count
        context['status_distribution'] = status_distribution
        
        return context


class EmployeeActivationView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle employee activation/deactivation"""
    log_action = 'Changed Employee Status'
    
    def post(self, request, pk, *args, **kwargs):
        """Toggle employee active status"""
        try:
            employee = get_object_or_404(Employee, pk=pk)
            action = request.POST.get('action')
            
            if action == 'activate':
                employee.is_active = True
                employee.user.is_active = True
                employee.save()
                employee.user.save()
                messages.success(request, f'Employee "{employee.user.get_full_name()}" activated successfully.')
                
            elif action == 'deactivate':
                # Check for pending appointments
                from appointments.models import Appointment
                pending_appointments = Appointment.objects.filter(
                    employee=employee,
                    status__in=['pending', 'confirmed']
                ).count()
                
                if pending_appointments > 0:
                    messages.warning(
                        request, 
                        f'Employee has {pending_appointments} pending appointment(s). '
                        'Please reassign or complete them before deactivating.'
                    )
                else:
                    employee.is_active = False
                    employee.user.is_active = False
                    employee.save()
                    employee.user.save()
                    messages.success(request, f'Employee "{employee.user.get_full_name()}" deactivated successfully.')
            
            else:
                messages.error(request, 'Invalid action.')
            
        except Exception as e:
            messages.error(request, f'Error updating employee status: {str(e)}')
        
        return redirect('admin_panel:employee_list')


class EmployeeBulkActionView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle bulk actions on employees"""
    log_action = 'Performed Bulk Employee Action'
    
    def post(self, request, *args, **kwargs):
        form = EmployeeBulkActionForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            employee_ids = form.cleaned_data['selected_employees']
            new_specialization = form.cleaned_data.get('new_specialization')
            
            employees = Employee.objects.filter(id__in=employee_ids)
            count = employees.count()
            
            if action == 'activate':
                employees.update(is_active=True)
                # Also activate user accounts
                User.objects.filter(employee_profile__in=employees).update(is_active=True)
                messages.success(request, f'{count} employee(s) activated successfully.')
                
            elif action == 'deactivate':
                # Check for pending appointments
                from appointments.models import Appointment
                employees_with_appointments = []
                for employee in employees:
                    pending_count = Appointment.objects.filter(
                        employee=employee,
                        status__in=['pending', 'confirmed']
                    ).count()
                    if pending_count > 0:
                        employees_with_appointments.append(f"{employee.user.get_full_name()} ({pending_count} appointments)")
                
                if employees_with_appointments:
                    messages.warning(
                        request, 
                        f'Cannot deactivate employees with pending appointments: {", ".join(employees_with_appointments)}'
                    )
                else:
                    employees.update(is_active=False)
                    # Also deactivate user accounts
                    User.objects.filter(employee_profile__in=employees).update(is_active=False)
                    messages.success(request, f'{count} employee(s) deactivated successfully.')
                    
            elif action == 'change_specialization' and new_specialization:
                employees.update(specialization=new_specialization)
                messages.success(
                    request, 
                    f'{count} employee(s) specialization updated to "{new_specialization}" successfully.'
                )
        else:
            messages.error(request, 'Invalid bulk action request.')
        
        return redirect('admin_panel:employee_list')


class EmployeeDetailAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for employee details"""
    
    def get(self, request, pk, *args, **kwargs):
        """Return employee details as JSON"""
        try:
            employee = get_object_or_404(Employee.objects.select_related('user'), pk=pk)
            
            # Get appointment statistics
            from appointments.models import Appointment
            appointments = Appointment.objects.filter(employee=employee)
            total_appointments = appointments.count()
            completed_appointments = appointments.filter(status='completed').count()
            
            data = {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'user': {
                    'id': employee.user.id,
                    'username': employee.user.username,
                    'email': employee.user.email,
                    'first_name': employee.user.first_name,
                    'last_name': employee.user.last_name,
                    'full_name': employee.user.get_full_name(),
                    'phone_number': employee.user.phone_number,
                    'address': employee.user.address,
                    'is_active': employee.user.is_active,
                },
                'specialization': employee.specialization,
                'hire_date': employee.hire_date.isoformat(),
                'is_active': employee.is_active,
                'performance': {
                    'total_appointments': total_appointments,
                    'completed_appointments': completed_appointments,
                    'completion_rate': (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0,
                }
            }
            
            return JsonResponse({
                'success': True,
                'employee': data
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


# System Settings Management Views

class SystemSettingsListView(SuperUserRequiredMixin, AdminLogMixin, ListView):
    """List view for system settings with search and filtering"""
    model = SystemSettings
    template_name = 'admin_panel/settings/settings_list.html'
    context_object_name = 'settings'
    paginate_by = 20
    log_action = 'Viewed System Settings'
    
    def get_queryset(self):
        """Filter settings based on search and category parameters"""
        queryset = SystemSettings.objects.select_related('updated_by')
        
        # Get search and filter parameters
        search_query = self.request.GET.get('search', '').strip()
        category = self.request.GET.get('category', '').strip()
        
        # Apply search filter
        if search_query:
            queryset = queryset.filter(
                Q(key__icontains=search_query) |
                Q(value__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Apply category filter
        if category:
            if category == 'time_slots':
                queryset = queryset.filter(key__contains='time_slot')
            elif category == 'appointments':
                queryset = queryset.filter(key__contains='appointment')
            elif category == 'notifications':
                queryset = queryset.filter(
                    Q(key__contains='notification') | 
                    Q(key__contains='email') | 
                    Q(key__contains='sms')
                )
            elif category == 'system':
                queryset = queryset.filter(
                    Q(key__contains='system') | 
                    Q(key__contains='debug') | 
                    Q(key__contains='maintenance')
                )
            elif category == 'email':
                queryset = queryset.filter(key__contains='email')
            elif category == 'other':
                # Settings that don't match common categories
                queryset = queryset.exclude(
                    Q(key__contains='time_slot') |
                    Q(key__contains='appointment') |
                    Q(key__contains='notification') |
                    Q(key__contains='email') |
                    Q(key__contains='sms') |
                    Q(key__contains='system') |
                    Q(key__contains='debug') |
                    Q(key__contains='maintenance')
                )
        
        return queryset.order_by('key')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'System Settings'
        
        # Import forms here to avoid circular imports
        from .forms import SystemSettingsSearchForm, SystemSettingsBulkActionForm
        context['search_form'] = SystemSettingsSearchForm(self.request.GET)
        context['bulk_form'] = SystemSettingsBulkActionForm()
        
        # Add statistics
        context['total_settings'] = SystemSettings.objects.count()
        context['categories'] = self._get_setting_categories()
        
        return context
    
    def _get_setting_categories(self):
        """Get setting categories with counts"""
        categories = {
            'time_slots': SystemSettings.objects.filter(key__contains='time_slot').count(),
            'appointments': SystemSettings.objects.filter(key__contains='appointment').count(),
            'notifications': SystemSettings.objects.filter(
                Q(key__contains='notification') | 
                Q(key__contains='email') | 
                Q(key__contains='sms')
            ).count(),
            'system': SystemSettings.objects.filter(
                Q(key__contains='system') | 
                Q(key__contains='debug') | 
                Q(key__contains='maintenance')
            ).count(),
        }
        return categories


class SystemSettingsCreateView(SuperUserRequiredMixin, AdminLogMixin, CreateView):
    """Create view for system settings"""
    model = SystemSettings
    template_name = 'admin_panel/settings/settings_form.html'
    success_url = reverse_lazy('admin_panel:settings_list')
    log_action = 'Created System Setting'
    
    def get_form_class(self):
        from .forms import SystemSettingsForm
        return SystemSettingsForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Create System Setting'
        context['form_action'] = 'Create'
        return context
    
    def form_valid(self, form):
        # Set the updated_by field to current user
        form.instance.updated_by = self.request.user
        messages.success(self.request, f'Setting "{form.instance.key}" created successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class SystemSettingsUpdateView(SuperUserRequiredMixin, AdminLogMixin, UpdateView):
    """Update view for system settings"""
    model = SystemSettings
    template_name = 'admin_panel/settings/settings_form.html'
    success_url = reverse_lazy('admin_panel:settings_list')
    log_action = 'Updated System Setting'
    
    def get_form_class(self):
        from .forms import SystemSettingsForm
        return SystemSettingsForm
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit Setting: {self.object.key}'
        context['form_action'] = 'Update'
        return context
    
    def form_valid(self, form):
        # Set the updated_by field to current user
        form.instance.updated_by = self.request.user
        messages.success(self.request, f'Setting "{form.instance.key}" updated successfully.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


class SystemSettingsDeleteView(SuperUserRequiredMixin, AdminLogMixin, DeleteView):
    """Delete view for system settings"""
    model = SystemSettings
    template_name = 'admin_panel/settings/settings_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:settings_list')
    log_action = 'Deleted System Setting'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete Setting: {self.object.key}'
        return context
    
    def delete(self, request, *args, **kwargs):
        setting_key = self.get_object().key
        messages.success(request, f'Setting "{setting_key}" deleted successfully.')
        return super().delete(request, *args, **kwargs)


class SystemSettingsBulkActionView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Handle bulk actions on system settings"""
    log_action = 'Performed Bulk Settings Action'
    
    def post(self, request, *args, **kwargs):
        from .forms import SystemSettingsBulkActionForm
        form = SystemSettingsBulkActionForm(request.POST)
        
        if form.is_valid():
            action = form.cleaned_data['action']
            setting_ids = form.cleaned_data['selected_settings']
            
            settings = SystemSettings.objects.filter(id__in=setting_ids)
            count = settings.count()
            
            if action == 'reset_selected':
                # Reset to default values (this would need a defaults system)
                messages.info(request, f'Reset functionality for {count} setting(s) - feature to be implemented.')
                
            elif action == 'delete_selected':
                setting_keys = [s.key for s in settings]
                settings.delete()
                messages.success(request, f'Deleted settings: {", ".join(setting_keys)}')
                
            elif action == 'export_selected':
                # Export settings as JSON
                return self._export_settings(settings)
        else:
            messages.error(request, 'Invalid bulk action request.')
        
        return redirect('admin_panel:settings_list')
    
    def _export_settings(self, settings):
        """Export settings as JSON file"""
        import json
        from django.http import HttpResponse
        
        settings_data = {}
        for setting in settings:
            settings_data[setting.key] = {
                'value': setting.value,
                'description': setting.description,
                'updated_at': setting.updated_at.isoformat(),
                'updated_by': setting.updated_by.username
            }
        
        response = HttpResponse(
            json.dumps(settings_data, indent=2),
            content_type='application/json'
        )
        response['Content-Disposition'] = 'attachment; filename="system_settings.json"'
        return response


class SettingsImportView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Import settings from JSON file"""
    log_action = 'Imported System Settings'
    
    def post(self, request, *args, **kwargs):
        from .forms import SettingsImportForm
        form = SettingsImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            json_file = form.cleaned_data['json_file']
            overwrite_existing = form.cleaned_data['overwrite_existing']
            
            try:
                import json
                content = json_file.read().decode('utf-8')
                settings_data = json.loads(content)
                
                created_count = 0
                updated_count = 0
                errors = []
                
                for key, setting_data in settings_data.items():
                    try:
                        value = setting_data.get('value', '')
                        description = setting_data.get('description', '')
                        
                        existing = SystemSettings.objects.filter(key=key).first()
                        
                        if existing:
                            if overwrite_existing:
                                existing.value = value
                                existing.description = description
                                existing.updated_by = request.user
                                existing.save()
                                updated_count += 1
                        else:
                            SystemSettings.objects.create(
                                key=key,
                                value=value,
                                description=description,
                                updated_by=request.user
                            )
                            created_count += 1
                            
                    except Exception as e:
                        errors.append(f'Error processing setting "{key}": {str(e)}')
                
                if errors:
                    messages.warning(
                        request, 
                        f'Import completed with errors. Created: {created_count}, Updated: {updated_count}. Errors: {"; ".join(errors)}'
                    )
                else:
                    messages.success(
                        request, 
                        f'Settings imported successfully. Created: {created_count}, Updated: {updated_count}.'
                    )
                    
            except Exception as e:
                messages.error(request, f'Error importing settings: {str(e)}')
        else:
            messages.error(request, 'Invalid import file.')
        
        return redirect('admin_panel:settings_list')


class TimeSlotSettingsView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """View for managing time slot settings"""
    template_name = 'admin_panel/settings/time_slot_settings.html'
    log_action = 'Viewed Time Slot Settings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Time Slot Settings'
        
        # Get current time slot settings
        from .forms import TimeSlotSettingsForm
        current_settings = self._get_current_time_slot_settings()
        context['form'] = TimeSlotSettingsForm(initial=current_settings)
        
        return context
    
    def post(self, request, *args, **kwargs):
        from .forms import TimeSlotSettingsForm
        form = TimeSlotSettingsForm(request.POST)
        
        if form.is_valid():
            # Save time slot settings
            self._save_time_slot_settings(form.cleaned_data, request.user)
            messages.success(request, 'Time slot settings updated successfully.')
            return redirect('admin_panel:time_slot_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
    
    def _get_current_time_slot_settings(self):
        """Get current time slot settings from database"""
        settings = {}
        
        setting_mappings = {
            'slot_duration': 'time_slot_duration',
            'start_time': 'business_start_time',
            'end_time': 'business_end_time',
            'break_start': 'break_start_time',
            'break_end': 'break_end_time',
            'advance_booking_days': 'advance_booking_days'
        }
        
        for form_field, setting_key in setting_mappings.items():
            try:
                setting = SystemSettings.objects.get(key=setting_key)
                if form_field in ['start_time', 'end_time', 'break_start', 'break_end']:
                    # Convert time string to time object
                    from datetime import datetime
                    settings[form_field] = datetime.strptime(setting.value, '%H:%M').time()
                else:
                    settings[form_field] = int(setting.value) if setting.value.isdigit() else setting.value
            except SystemSettings.DoesNotExist:
                # Use default values if setting doesn't exist
                defaults = {
                    'slot_duration': 60,
                    'start_time': '09:00',
                    'end_time': '18:00',
                    'advance_booking_days': 30
                }
                if form_field in defaults:
                    if form_field in ['start_time', 'end_time']:
                        from datetime import datetime
                        settings[form_field] = datetime.strptime(defaults[form_field], '%H:%M').time()
                    else:
                        settings[form_field] = defaults[form_field]
        
        return settings
    
    def _save_time_slot_settings(self, cleaned_data, user):
        """Save time slot settings to database"""
        setting_mappings = {
            'slot_duration': 'time_slot_duration',
            'start_time': 'business_start_time',
            'end_time': 'business_end_time',
            'break_start': 'break_start_time',
            'break_end': 'break_end_time',
            'advance_booking_days': 'advance_booking_days'
        }
        
        for form_field, setting_key in setting_mappings.items():
            value = cleaned_data.get(form_field)
            if value is not None:
                if hasattr(value, 'strftime'):  # Time object
                    value = value.strftime('%H:%M')
                else:
                    value = str(value)
                
                setting, created = SystemSettings.objects.get_or_create(
                    key=setting_key,
                    defaults={
                        'value': value,
                        'description': f'Time slot setting: {form_field}',
                        'updated_by': user
                    }
                )
                
                if not created:
                    setting.value = value
                    setting.updated_by = user
                    setting.save()


class AppointmentSettingsView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """View for managing appointment settings"""
    template_name = 'admin_panel/settings/appointment_settings.html'
    log_action = 'Viewed Appointment Settings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Appointment Settings'
        
        # Get current appointment settings
        from .forms import AppointmentSettingsForm
        current_settings = self._get_current_appointment_settings()
        context['form'] = AppointmentSettingsForm(initial=current_settings)
        
        return context
    
    def post(self, request, *args, **kwargs):
        from .forms import AppointmentSettingsForm
        form = AppointmentSettingsForm(request.POST)
        
        if form.is_valid():
            # Save appointment settings
            self._save_appointment_settings(form.cleaned_data, request.user)
            messages.success(request, 'Appointment settings updated successfully.')
            return redirect('admin_panel:appointment_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
    
    def _get_current_appointment_settings(self):
        """Get current appointment settings from database"""
        settings = {}
        
        setting_mappings = {
            'max_appointments_per_slot': 'max_appointments_per_slot',
            'cancellation_deadline_hours': 'cancellation_deadline_hours',
            'auto_confirm_appointments': 'auto_confirm_appointments',
            'send_reminder_notifications': 'send_reminder_notifications',
            'reminder_hours_before': 'reminder_hours_before',
            'require_employee_assignment': 'require_employee_assignment'
        }
        
        for form_field, setting_key in setting_mappings.items():
            try:
                setting = SystemSettings.objects.get(key=setting_key)
                if form_field in ['auto_confirm_appointments', 'send_reminder_notifications', 'require_employee_assignment']:
                    settings[form_field] = setting.value.lower() in ['true', '1', 'yes']
                else:
                    settings[form_field] = int(setting.value) if setting.value.isdigit() else setting.value
            except SystemSettings.DoesNotExist:
                # Use default values
                defaults = {
                    'max_appointments_per_slot': 1,
                    'cancellation_deadline_hours': 24,
                    'auto_confirm_appointments': False,
                    'send_reminder_notifications': True,
                    'reminder_hours_before': 24,
                    'require_employee_assignment': True
                }
                if form_field in defaults:
                    settings[form_field] = defaults[form_field]
        
        return settings
    
    def _save_appointment_settings(self, cleaned_data, user):
        """Save appointment settings to database"""
        setting_mappings = {
            'max_appointments_per_slot': 'max_appointments_per_slot',
            'cancellation_deadline_hours': 'cancellation_deadline_hours',
            'auto_confirm_appointments': 'auto_confirm_appointments',
            'send_reminder_notifications': 'send_reminder_notifications',
            'reminder_hours_before': 'reminder_hours_before',
            'require_employee_assignment': 'require_employee_assignment'
        }
        
        for form_field, setting_key in setting_mappings.items():
            value = cleaned_data.get(form_field)
            if value is not None:
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                else:
                    value = str(value)
                
                setting, created = SystemSettings.objects.get_or_create(
                    key=setting_key,
                    defaults={
                        'value': value,
                        'description': f'Appointment setting: {form_field}',
                        'updated_by': user
                    }
                )
                
                if not created:
                    setting.value = value
                    setting.updated_by = user
                    setting.save()


class NotificationSettingsView(SuperUserRequiredMixin, AdminLogMixin, TemplateView):
    """View for managing notification settings"""
    template_name = 'admin_panel/settings/notification_settings.html'
    log_action = 'Viewed Notification Settings'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Notification Settings'
        
        # Get current notification settings
        from .forms import NotificationSettingsForm
        current_settings = self._get_current_notification_settings()
        context['form'] = NotificationSettingsForm(initial=current_settings)
        
        return context
    
    def post(self, request, *args, **kwargs):
        from .forms import NotificationSettingsForm
        form = NotificationSettingsForm(request.POST)
        
        if form.is_valid():
            # Save notification settings
            self._save_notification_settings(form.cleaned_data, request.user)
            messages.success(request, 'Notification settings updated successfully.')
            return redirect('admin_panel:notification_settings')
        else:
            messages.error(request, 'Please correct the errors below.')
            context = self.get_context_data(**kwargs)
            context['form'] = form
            return self.render_to_response(context)
    
    def _get_current_notification_settings(self):
        """Get current notification settings from database"""
        settings = {}
        
        setting_mappings = {
            'admin_email': 'admin_email',
            'from_email': 'from_email',
            'email_notifications_enabled': 'email_notifications_enabled',
            'sms_notifications_enabled': 'sms_notifications_enabled',
            'notify_new_appointments': 'notify_new_appointments',
            'notify_cancellations': 'notify_cancellations',
            'notify_employee_assignments': 'notify_employee_assignments'
        }
        
        for form_field, setting_key in setting_mappings.items():
            try:
                setting = SystemSettings.objects.get(key=setting_key)
                if form_field in ['email_notifications_enabled', 'sms_notifications_enabled', 
                                'notify_new_appointments', 'notify_cancellations', 'notify_employee_assignments']:
                    settings[form_field] = setting.value.lower() in ['true', '1', 'yes']
                else:
                    settings[form_field] = setting.value
            except SystemSettings.DoesNotExist:
                # Use default values
                defaults = {
                    'admin_email': 'admin@example.com',
                    'from_email': 'noreply@example.com',
                    'email_notifications_enabled': True,
                    'sms_notifications_enabled': False,
                    'notify_new_appointments': True,
                    'notify_cancellations': True,
                    'notify_employee_assignments': True
                }
                if form_field in defaults:
                    settings[form_field] = defaults[form_field]
        
        return settings
    
    def _save_notification_settings(self, cleaned_data, user):
        """Save notification settings to database"""
        setting_mappings = {
            'admin_email': 'admin_email',
            'from_email': 'from_email',
            'email_notifications_enabled': 'email_notifications_enabled',
            'sms_notifications_enabled': 'sms_notifications_enabled',
            'notify_new_appointments': 'notify_new_appointments',
            'notify_cancellations': 'notify_cancellations',
            'notify_employee_assignments': 'notify_employee_assignments'
        }
        
        for form_field, setting_key in setting_mappings.items():
            value = cleaned_data.get(form_field)
            if value is not None:
                if isinstance(value, bool):
                    value = 'true' if value else 'false'
                else:
                    value = str(value)
                
                setting, created = SystemSettings.objects.get_or_create(
                    key=setting_key,
                    defaults={
                        'value': value,
                        'description': f'Notification setting: {form_field}',
                        'updated_by': user
                    }
                )
                
                if not created:
                    setting.value = value
                    setting.updated_by = user
                    setting.save()


class SettingsResetView(SuperUserRequiredMixin, AdminLogMixin, View):
    """Reset settings to default values"""
    log_action = 'Reset System Settings'
    
    def post(self, request, *args, **kwargs):
        """Reset all or specific settings to defaults"""
        reset_type = request.POST.get('reset_type', 'all')
        
        try:
            if reset_type == 'time_slots':
                self._reset_time_slot_settings(request.user)
                messages.success(request, 'Time slot settings reset to defaults.')
            elif reset_type == 'appointments':
                self._reset_appointment_settings(request.user)
                messages.success(request, 'Appointment settings reset to defaults.')
            elif reset_type == 'notifications':
                self._reset_notification_settings(request.user)
                messages.success(request, 'Notification settings reset to defaults.')
            elif reset_type == 'all':
                self._reset_all_settings(request.user)
                messages.success(request, 'All settings reset to defaults.')
            else:
                messages.error(request, 'Invalid reset type.')
                
        except Exception as e:
            messages.error(request, f'Error resetting settings: {str(e)}')
        
        return redirect('admin_panel:settings_list')
    
    def _reset_time_slot_settings(self, user):
        """Reset time slot settings to defaults"""
        defaults = {
            'time_slot_duration': ('60', 'Duration of each time slot in minutes'),
            'business_start_time': ('09:00', 'Business start time'),
            'business_end_time': ('18:00', 'Business end time'),
            'advance_booking_days': ('30', 'Days in advance customers can book')
        }
        
        for key, (value, description) in defaults.items():
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description, 'updated_by': user}
            )
            if not created:
                setting.value = value
                setting.description = description
                setting.updated_by = user
                setting.save()
    
    def _reset_appointment_settings(self, user):
        """Reset appointment settings to defaults"""
        defaults = {
            'max_appointments_per_slot': ('1', 'Maximum appointments per time slot'),
            'cancellation_deadline_hours': ('24', 'Hours before appointment when cancellation is allowed'),
            'auto_confirm_appointments': ('false', 'Automatically confirm new appointments'),
            'send_reminder_notifications': ('true', 'Send reminder notifications to customers'),
            'reminder_hours_before': ('24', 'Hours before appointment to send reminder'),
            'require_employee_assignment': ('true', 'Require employee assignment for appointments')
        }
        
        for key, (value, description) in defaults.items():
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description, 'updated_by': user}
            )
            if not created:
                setting.value = value
                setting.description = description
                setting.updated_by = user
                setting.save()
    
    def _reset_notification_settings(self, user):
        """Reset notification settings to defaults"""
        defaults = {
            'admin_email': ('admin@example.com', 'Email address for admin notifications'),
            'from_email': ('noreply@example.com', 'From email address for system notifications'),
            'email_notifications_enabled': ('true', 'Enable email notifications'),
            'sms_notifications_enabled': ('false', 'Enable SMS notifications'),
            'notify_new_appointments': ('true', 'Notify admin of new appointments'),
            'notify_cancellations': ('true', 'Notify admin of appointment cancellations'),
            'notify_employee_assignments': ('true', 'Notify employees of new assignments')
        }
        
        for key, (value, description) in defaults.items():
            setting, created = SystemSettings.objects.get_or_create(
                key=key,
                defaults={'value': value, 'description': description, 'updated_by': user}
            )
            if not created:
                setting.value = value
                setting.description = description
                setting.updated_by = user
                setting.save()
    
    def _reset_all_settings(self, user):
        """Reset all settings to defaults"""
        self._reset_time_slot_settings(user)
        self._reset_appointment_settings(user)
        self._reset_notification_settings(user)

# Additional AJAX Endpoints for Enhanced Functionality

class ServiceSearchAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for service search and filtering"""
    
    def get(self, request, *args, **kwargs):
        """Return filtered services as JSON"""
        try:
            search_query = request.GET.get('q', '').strip()
            category_id = request.GET.get('category', '').strip()
            status = request.GET.get('status', '').strip()
            limit = int(request.GET.get('limit', 10))
            
            queryset = Service.objects.select_related('category')
            
            # Apply search filter
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__name__icontains=search_query)
                )
            
            # Apply category filter
            if category_id:
                try:
                    queryset = queryset.filter(category_id=int(category_id))
                except ValueError:
                    pass
            
            # Apply status filter
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            
            # Limit results
            services = queryset[:limit]
            
            results = []
            for service in services:
                results.append({
                    'id': service.id,
                    'name': service.name,
                    'category': service.category.name,
                    'base_price': str(service.base_price),
                    'is_active': service.is_active,
                    'image_url': service.image.url if service.image else None
                })
            
            return JsonResponse({
                'success': True,
                'services': results,
                'total': queryset.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class CategorySearchAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for category search and filtering"""
    
    def get(self, request, *args, **kwargs):
        """Return filtered categories as JSON"""
        try:
            search_query = request.GET.get('q', '').strip()
            status = request.GET.get('status', '').strip()
            limit = int(request.GET.get('limit', 10))
            
            queryset = ServiceCategory.objects.annotate(service_count=Count('services'))
            
            # Apply search filter
            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query)
                )
            
            # Apply status filter
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            
            # Limit results
            categories = queryset[:limit]
            
            results = []
            for category in categories:
                results.append({
                    'id': category.id,
                    'name': category.name,
                    'description': category.description,
                    'icon': category.icon,
                    'is_active': category.is_active,
                    'service_count': category.service_count
                })
            
            return JsonResponse({
                'success': True,
                'categories': results,
                'total': queryset.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class EmployeeSearchAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for employee search and filtering"""
    
    def get(self, request, *args, **kwargs):
        """Return filtered employees as JSON"""
        try:
            search_query = request.GET.get('q', '').strip()
            status = request.GET.get('status', '').strip()
            specialization = request.GET.get('specialization', '').strip()
            limit = int(request.GET.get('limit', 10))
            
            queryset = Employee.objects.select_related('user')
            
            # Apply search filter
            if search_query:
                queryset = queryset.filter(
                    Q(user__first_name__icontains=search_query) |
                    Q(user__last_name__icontains=search_query) |
                    Q(user__username__icontains=search_query) |
                    Q(user__email__icontains=search_query) |
                    Q(employee_id__icontains=search_query) |
                    Q(specialization__icontains=search_query)
                )
            
            # Apply status filter
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'inactive':
                queryset = queryset.filter(is_active=False)
            
            # Apply specialization filter
            if specialization:
                queryset = queryset.filter(specialization__icontains=specialization)
            
            # Limit results
            employees = queryset[:limit]
            
            results = []
            for employee in employees:
                results.append({
                    'id': employee.id,
                    'employee_id': employee.employee_id,
                    'name': employee.user.get_full_name(),
                    'email': employee.user.email,
                    'specialization': employee.specialization,
                    'is_active': employee.is_active,
                    'hire_date': employee.hire_date.isoformat() if employee.hire_date else None
                })
            
            return JsonResponse({
                'success': True,
                'employees': results,
                'total': queryset.count()
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class DashboardChartsAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for dashboard chart data"""
    
    def get(self, request, *args, **kwargs):
        """Return chart data as JSON"""
        try:
            chart_type = request.GET.get('type', 'appointments')
            days = int(request.GET.get('days', 30))
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            if chart_type == 'appointments':
                return self._get_appointment_chart_data(start_date, end_date)
            elif chart_type == 'revenue':
                return self._get_revenue_chart_data(start_date, end_date)
            elif chart_type == 'services':
                return self._get_service_chart_data(start_date, end_date)
            elif chart_type == 'employees':
                return self._get_employee_chart_data()
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid chart type'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _get_appointment_chart_data(self, start_date, end_date):
        """Get appointment trend data"""
        from appointments.models import Appointment
        
        # Get daily appointment counts
        appointments = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(appointment_date)'}
        ).values('day').annotate(
            count=Count('id')
        ).order_by('day')
        
        labels = []
        data = []
        
        # Fill in missing days with 0
        current_date = start_date
        appointment_dict = {item['day']: item['count'] for item in appointments}
        
        while current_date <= end_date:
            labels.append(current_date.strftime('%Y-%m-%d'))
            data.append(appointment_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'success': True,
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Appointments',
                    'data': data,
                    'borderColor': '#0d6efd',
                    'backgroundColor': 'rgba(13, 110, 253, 0.1)',
                    'tension': 0.4
                }]
            }
        })
    
    def _get_revenue_chart_data(self, start_date, end_date):
        """Get revenue trend data"""
        from appointments.models import Appointment
        
        # Get daily revenue (assuming appointments have a price field)
        revenue_data = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date],
            status='completed'
        ).extra(
            select={'day': 'date(appointment_date)'}
        ).values('day').annotate(
            revenue=Sum('service__base_price')
        ).order_by('day')
        
        labels = []
        data = []
        
        # Fill in missing days with 0
        current_date = start_date
        revenue_dict = {item['day']: float(item['revenue'] or 0) for item in revenue_data}
        
        while current_date <= end_date:
            labels.append(current_date.strftime('%Y-%m-%d'))
            data.append(revenue_dict.get(current_date, 0))
            current_date += timedelta(days=1)
        
        return JsonResponse({
            'success': True,
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Revenue (₹)',
                    'data': data,
                    'borderColor': '#198754',
                    'backgroundColor': 'rgba(25, 135, 84, 0.1)',
                    'tension': 0.4
                }]
            }
        })
    
    def _get_service_chart_data(self, start_date, end_date):
        """Get service popularity data"""
        from appointments.models import Appointment
        
        # Get most popular services
        service_data = Appointment.objects.filter(
            appointment_date__range=[start_date, end_date]
        ).values(
            'service__name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        labels = [item['service__name'] for item in service_data]
        data = [item['count'] for item in service_data]
        
        return JsonResponse({
            'success': True,
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Appointments',
                    'data': data,
                    'backgroundColor': [
                        '#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#dc3545',
                        '#fd7e14', '#ffc107', '#198754', '#20c997', '#0dcaf0'
                    ]
                }]
            }
        })
    
    def _get_employee_chart_data(self):
        """Get employee workload data"""
        from appointments.models import Appointment
        
        # Get employee workload for current month
        start_date = timezone.now().replace(day=1).date()
        
        employee_data = Appointment.objects.filter(
            appointment_date__gte=start_date,
            assigned_employee__isnull=False
        ).values(
            'assigned_employee__user__first_name',
            'assigned_employee__user__last_name'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        labels = [f"{item['assigned_employee__user__first_name']} {item['assigned_employee__user__last_name']}" 
                 for item in employee_data]
        data = [item['count'] for item in employee_data]
        
        return JsonResponse({
            'success': True,
            'chart_data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Appointments',
                    'data': data,
                    'backgroundColor': '#fd7e14'
                }]
            }
        })


class QuickStatsAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for quick statistics updates"""
    
    def get(self, request, *args, **kwargs):
        """Return quick stats as JSON"""
        try:
            from appointments.models import Appointment
            
            today = timezone.now().date()
            
            # Today's stats
            today_appointments = Appointment.objects.filter(appointment_date=today).count()
            pending_appointments = Appointment.objects.filter(status='pending').count()
            
            # This month's stats
            month_start = today.replace(day=1)
            month_appointments = Appointment.objects.filter(
                appointment_date__gte=month_start
            ).count()
            
            # Revenue stats
            month_revenue = Appointment.objects.filter(
                appointment_date__gte=month_start,
                status='completed'
            ).aggregate(
                total=Sum('service__base_price')
            )['total'] or 0
            
            # Active counts
            active_services = Service.objects.filter(is_active=True).count()
            active_employees = Employee.objects.filter(is_active=True).count()
            active_categories = ServiceCategory.objects.filter(is_active=True).count()
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'today_appointments': today_appointments,
                    'pending_appointments': pending_appointments,
                    'month_appointments': month_appointments,
                    'month_revenue': float(month_revenue),
                    'active_services': active_services,
                    'active_employees': active_employees,
                    'active_categories': active_categories,
                    'last_updated': timezone.now().isoformat()
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)


class FormValidationAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for real-time form validation"""
    
    def post(self, request, *args, **kwargs):
        """Validate form fields in real-time"""
        try:
            form_type = request.POST.get('form_type')
            field_name = request.POST.get('field_name')
            field_value = request.POST.get('field_value', '').strip()
            exclude_id = request.POST.get('exclude_id')  # For updates
            
            if not all([form_type, field_name, field_value]):
                return JsonResponse({
                    'success': False,
                    'error': 'Missing required parameters'
                }, status=400)
            
            validation_result = self._validate_field(
                form_type, field_name, field_value, exclude_id
            )
            
            return JsonResponse({
                'success': True,
                'valid': validation_result['valid'],
                'message': validation_result['message']
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def _validate_field(self, form_type, field_name, field_value, exclude_id=None):
        """Validate specific form fields"""
        
        if form_type == 'service':
            if field_name == 'name':
                query = Service.objects.filter(name__iexact=field_value)
                if exclude_id:
                    try:
                        query = query.exclude(pk=int(exclude_id))
                    except ValueError:
                        pass
                
                if query.exists():
                    return {'valid': False, 'message': 'Service name already exists'}
                return {'valid': True, 'message': 'Service name is available'}
                
        elif form_type == 'category':
            if field_name == 'name':
                query = ServiceCategory.objects.filter(name__iexact=field_value)
                if exclude_id:
                    try:
                        query = query.exclude(pk=int(exclude_id))
                    except ValueError:
                        pass
                
                if query.exists():
                    return {'valid': False, 'message': 'Category name already exists'}
                return {'valid': True, 'message': 'Category name is available'}
                
        elif form_type == 'employee':
            if field_name == 'username':
                query = User.objects.filter(username__iexact=field_value)
                if exclude_id:
                    try:
                        employee = Employee.objects.get(pk=int(exclude_id))
                        query = query.exclude(pk=employee.user.pk)
                    except (ValueError, Employee.DoesNotExist):
                        pass
                
                if query.exists():
                    return {'valid': False, 'message': 'Username already exists'}
                return {'valid': True, 'message': 'Username is available'}
                
            elif field_name == 'email':
                query = User.objects.filter(email__iexact=field_value)
                if exclude_id:
                    try:
                        employee = Employee.objects.get(pk=int(exclude_id))
                        query = query.exclude(pk=employee.user.pk)
                    except (ValueError, Employee.DoesNotExist):
                        pass
                
                if query.exists():
                    return {'valid': False, 'message': 'Email already exists'}
                return {'valid': True, 'message': 'Email is available'}
                
            elif field_name == 'employee_id':
                query = Employee.objects.filter(employee_id__iexact=field_value)
                if exclude_id:
                    try:
                        query = query.exclude(pk=int(exclude_id))
                    except ValueError:
                        pass
                
                if query.exists():
                    return {'valid': False, 'message': 'Employee ID already exists'}
                return {'valid': True, 'message': 'Employee ID is available'}
        
        return {'valid': True, 'message': 'Field is valid'}


class NotificationAjaxView(SuperUserRequiredMixin, AjaxResponseMixin, View):
    """AJAX endpoint for real-time notifications"""
    
    def get(self, request, *args, **kwargs):
        """Get recent notifications"""
        try:
            from appointments.models import Appointment
            
            # Get recent activities (last 24 hours)
            yesterday = timezone.now() - timedelta(hours=24)
            
            notifications = []
            
            # New appointments
            new_appointments = Appointment.objects.filter(
                created_at__gte=yesterday,
                status='pending'
            ).select_related('service', 'customer').order_by('-created_at')[:5]
            
            for appointment in new_appointments:
                notifications.append({
                    'type': 'new_appointment',
                    'title': 'New Appointment',
                    'message': f'{appointment.customer.get_full_name()} booked {appointment.service.name}',
                    'timestamp': appointment.created_at.isoformat(),
                    'url': f'/admin/appointments/{appointment.id}/'
                })
            
            # Recent cancellations
            cancelled_appointments = Appointment.objects.filter(
                updated_at__gte=yesterday,
                status='cancelled'
            ).select_related('service', 'customer').order_by('-updated_at')[:3]
            
            for appointment in cancelled_appointments:
                notifications.append({
                    'type': 'cancellation',
                    'title': 'Appointment Cancelled',
                    'message': f'{appointment.customer.get_full_name()} cancelled {appointment.service.name}',
                    'timestamp': appointment.updated_at.isoformat(),
                    'url': f'/admin/appointments/{appointment.id}/'
                })
            
            # Sort by timestamp
            notifications.sort(key=lambda x: x['timestamp'], reverse=True)
            
            return JsonResponse({
                'success': True,
                'notifications': notifications[:10],  # Limit to 10 most recent
                'unread_count': len(notifications)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)