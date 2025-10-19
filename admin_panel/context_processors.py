from django.urls import reverse, NoReverseMatch


def admin_panel_context(request):
    """
    Context processor to provide admin panel URLs and utilities
    throughout the application templates.
    """
    context = {}
    
    # Only add admin panel context for authenticated super users
    if request.user.is_authenticated and request.user.is_superuser:
        try:
            context.update({
                'admin_panel_urls': {
                    'dashboard': reverse('admin_panel:dashboard'),
                    'service_list': reverse('admin_panel:service_list'),
                    'service_create': reverse('admin_panel:service_create'),
                    'category_list': reverse('admin_panel:category_list'),
                    'employee_list': reverse('admin_panel:employee_list'),
                    'employee_create': reverse('admin_panel:employee_create'),
                    'pricing_matrix': reverse('admin_panel:pricing_matrix'),
                    'settings_list': reverse('admin_panel:settings_list'),
                    'logs': reverse('admin_panel:logs'),
                },
                'is_super_admin': True,
            })
        except NoReverseMatch:
            # Handle case where admin panel URLs are not available
            context['is_super_admin'] = False
    else:
        context['is_super_admin'] = False
    
    return context


def admin_quick_actions(request):
    """
    Context processor to provide quick admin actions based on current page.
    """
    context = {'admin_quick_actions': []}
    
    if not (request.user.is_authenticated and request.user.is_superuser):
        return context
    
    # Determine quick actions based on current URL
    current_url = request.resolver_match
    if current_url:
        url_name = current_url.url_name
        namespace = current_url.namespace
        
        try:
            if namespace == 'services':
                if url_name == 'service_list':
                    context['admin_quick_actions'] = [
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
                    ]
                elif url_name == 'service_detail':
                    service_id = current_url.kwargs.get('pk')
                    if service_id:
                        context['admin_quick_actions'] = [
                            {
                                'name': 'Edit Service',
                                'url': reverse('admin_panel:service_update', args=[service_id]),
                                'icon': 'fas fa-edit',
                                'class': 'btn-outline-warning'
                            },
                            {
                                'name': 'Manage Pricing',
                                'url': f"{reverse('admin_panel:pricing_matrix')}?service={service_id}",
                                'icon': 'fas fa-dollar-sign',
                                'class': 'btn-outline-info'
                            }
                        ]
            
            elif namespace == 'accounts':
                if url_name in ['employee_dashboard', 'admin_dashboard']:
                    context['admin_quick_actions'] = [
                        {
                            'name': 'Admin Panel',
                            'url': reverse('admin_panel:dashboard'),
                            'icon': 'fas fa-cogs',
                            'class': 'btn-outline-primary'
                        },
                        {
                            'name': 'Manage Employees',
                            'url': reverse('admin_panel:employee_list'),
                            'icon': 'fas fa-users',
                            'class': 'btn-outline-info'
                        }
                    ]
        except NoReverseMatch:
            pass
    
    return context