"""
Admin panel decorators for permission control and logging
"""
from functools import wraps
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render


def super_user_required(view_func):
    """
    Decorator for function-based views that requires super user access.
    Combines login_required with super user check.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_superuser:
            return render(request, 'admin_panel/403.html', {
                'error_message': 'You must be a super user to access this page.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def ajax_required(view_func):
    """
    Decorator that ensures the request is an AJAX request
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return HttpResponseForbidden('AJAX request required')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def log_admin_action(action_name):
    """
    Decorator that logs admin actions for audit trail
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Import here to avoid circular imports
            from .utils import log_admin_action as log_action
            
            response = view_func(request, *args, **kwargs)
            
            # Log the action after successful execution
            if hasattr(response, 'status_code') and 200 <= response.status_code < 400:
                log_action(
                    user=request.user,
                    action=action_name,
                    request=request,
                    view_kwargs=kwargs
                )
            
            return response
        return _wrapped_view
    return decorator