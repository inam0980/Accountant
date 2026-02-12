from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect


@csrf_protect
@never_cache
def login_view(request):
    """
    Single login page for all roles
    Auto-detects role after login and redirects to appropriate dashboard
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        # Get credentials from form
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Log the user in
                login(request, user)
                
                # Success message with role
                messages.success(
                    request,
                    f'Welcome back, {user.get_full_name() or user.username}! '
                    f'Logged in as {user.get_role_display()}.'
                )
                
                # Redirect to dashboard (role-based filtering happens in template)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(
                    request,
                    'Your account has been deactivated. Please contact the administrator.'
                )
        else:
            messages.error(
                request,
                'Invalid credentials. Please check your username/email and password.'
            )
    
    return render(request, 'accounts/login.html', {
        'next': request.GET.get('next', '/')
    })


@login_required
def logout_view(request):
    """
    Logout view - logs out the user and redirects to login page
    """
    user_name = request.user.get_full_name() or request.user.username
    logout(request)
    messages.success(request, f'You have been successfully logged out. Goodbye, {user_name}!')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """
    User profile view - displays current user information
    """
    return render(request, 'accounts/profile.html', {
        'user': request.user
    })
