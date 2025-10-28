from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Service, ServiceCategory
from appointments.models import Appointment


def service_list_view(request):
    """Display all available services"""
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    services = Service.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(category__name__icontains=search_query)
        )
    
    # Category filter
    category_id = request.GET.get('category')
    if category_id:
        services = services.filter(category_id=category_id)
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    services = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'services': services,
        'search_query': search_query,
        'selected_category': category_id,
    }
    
    return render(request, 'services/service_list.html', context)


def service_detail_view(request, service_id):
    """Display detailed information about a specific service"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    # Get related services from the same category
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(id=service.id)[:4]
    
    # Get pricing options if available
    pricing_options = service.prices.filter(is_active=True)
    
    context = {
        'service': service,
        'related_services': related_services,
        'pricing_options': pricing_options,
    }
    
    return render(request, 'services/service_detail.html', context)


@login_required
def book_service_view(request, service_id):
    """Book appointment for a specific service"""
    if not request.user.role == 'customer':
        messages.error(request, 'Only customers can book appointments. Employees should manage existing appointments.')
        return redirect('services:service_list')
    
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    if request.method == 'POST':
        from appointments.forms import AppointmentBookingForm
        form = AppointmentBookingForm(request.POST, user=request.user)
        if form.is_valid():
            # Create the appointment directly
            appointment = form.save(commit=False)
            appointment.customer = request.user
            appointment.selected_service = service  # Set the service from URL
            appointment.save()
            
            messages.success(request, f'Appointment booked successfully! Your appointment ID is #{appointment.id}')
            return redirect('appointments:appointment_detail', appointment_id=appointment.id)
    else:
        from appointments.forms import AppointmentBookingForm
        # Pre-populate the service field
        initial_data = {'selected_service': service}
        form = AppointmentBookingForm(user=request.user, initial=initial_data)
    
    context = {
        'service': service,
        'form': form,
    }
    
    return render(request, 'services/book_service.html', context)


def category_detail_view(request, category_id):
    """Display services in a specific category"""
    category = get_object_or_404(ServiceCategory, id=category_id, is_active=True)
    services = Service.objects.filter(category=category, is_active=True)
    
    # Search within category
    search_query = request.GET.get('search')
    if search_query:
        services = services.filter(
            Q(name__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(services, 12)
    page_number = request.GET.get('page')
    services = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'services': services,
        'search_query': search_query,
    }
    
    return render(request, 'services/category_detail.html', context)