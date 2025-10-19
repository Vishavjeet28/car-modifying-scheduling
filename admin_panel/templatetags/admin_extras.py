from django import template
from django.urls import reverse

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a value in a dictionary using a key.
    Usage: {{ dict|lookup:key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def multiply(value, arg):
    """
    Template filter to multiply two values.
    Usage: {{ value|multiply:arg }}
    """
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """
    Template filter to calculate percentage.
    Usage: {{ value|percentage:total }}
    """
    try:
        if float(total) == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except (ValueError, TypeError):
        return 0

@register.filter
def currency(value):
    """
    Template filter to format currency.
    Usage: {{ value|currency }}
    """
    try:
        return f"₹{float(value):,.2f}"
    except (ValueError, TypeError):
        return "₹0.00"

@register.inclusion_tag('admin_panel/breadcrumb.html', takes_context=True)
def admin_breadcrumb(context, *args):
    """
    Template tag to generate breadcrumb navigation.
    Usage: {% admin_breadcrumb "Services" "service_list" %}
    """
    request = context['request']
    breadcrumbs = [
        {'name': 'Admin', 'url': reverse('admin_panel:dashboard'), 'active': False}
    ]
    
    # Add breadcrumb items from arguments (name, url_name pairs)
    for i in range(0, len(args), 2):
        if i + 1 < len(args):
            name = args[i]
            url_name = args[i + 1]
            try:
                url = reverse(f'admin_panel:{url_name}')
                breadcrumbs.append({
                    'name': name,
                    'url': url,
                    'active': False
                })
            except:
                breadcrumbs.append({
                    'name': name,
                    'url': '#',
                    'active': False
                })
    
    # Mark the last item as active
    if breadcrumbs:
        breadcrumbs[-1]['active'] = True
    
    return {'breadcrumbs': breadcrumbs}

@register.simple_tag
def is_super_user(user):
    """
    Template tag to check if user is super user.
    Usage: {% is_super_user user as is_super %}
    """
    return user.is_authenticated and user.is_superuser

@register.inclusion_tag('admin_panel/quick_actions.html', takes_context=True)
def admin_quick_actions_widget(context, position='top-right'):
    """
    Template tag to render admin quick actions widget.
    Usage: {% admin_quick_actions_widget "top-right" %}
    """
    request = context['request']
    user = request.user
    
    if not (user.is_authenticated and user.is_superuser):
        return {'show_widget': False}
    
    quick_actions = context.get('admin_quick_actions', [])
    
    return {
        'show_widget': True,
        'quick_actions': quick_actions,
        'position': position,
        'user': user
    }