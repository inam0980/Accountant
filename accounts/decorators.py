"""
Custom decorators for role-based access control
"""

from functools import wraps
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.template.response import TemplateResponse

from .permissions import has_module_permission, has_action_permission


def role_required(*allowed_roles):
    """
    Decorator to restrict view access to specific roles
    
    Usage:
        @role_required('admin', 'teacher')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # Return 403 Forbidden page
            return TemplateResponse(
                request, 
                'accounts/403.html',
                {
                    'required_roles': allowed_roles,
                    'user_role': request.user.get_role_display()
                },
                status=403
            )
        return wrapper
    return decorator


def module_required(module_name):
    """
    Decorator to restrict view access based on module permissions
    
    Usage:
        @module_required('students')
        def student_list(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if has_module_permission(request.user, module_name):
                return view_func(request, *args, **kwargs)
            
            # Return 403 Forbidden page
            return TemplateResponse(
                request,
                'accounts/403.html',
                {
                    'module_name': module_name,
                    'user_role': request.user.get_role_display()
                },
                status=403
            )
        return wrapper
    return decorator


def action_required(module_name, action):
    """
    Decorator to restrict view access based on specific action permissions
    
    Usage:
        @action_required('students', 'create')
        def student_create(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            if has_action_permission(request.user, module_name, action):
                return view_func(request, *args, **kwargs)
            
            # Return 403 Forbidden page
            return TemplateResponse(
                request,
                'accounts/403.html',
                {
                    'module_name': module_name,
                    'action': action,
                    'user_role': request.user.get_role_display()
                },
                status=403
            )
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to restrict view to admin only
    
    Usage:
        @admin_required
        def admin_only_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.role == 'admin':
            return view_func(request, *args, **kwargs)
        
        return TemplateResponse(
            request,
            'accounts/403.html',
            {
                'required_roles': ['admin'],
                'user_role': request.user.get_role_display()
            },
            status=403
        )
    return wrapper
