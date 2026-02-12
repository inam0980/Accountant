from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from accounts.decorators import module_required

# Create your views here.

@login_required
def index(request):
    """
    Main dashboard view showing all 14 modules and quick statistics
    Filtered based on user role permissions (Accountant mode Only)
    """
    
    # Import models for statistics
    from students.models import Student
    from billing.models import Invoice, Payment
    from accounts.models import CustomUser
    from django.db.models import Sum
    from accounts.permissions import get_user_modules
    
    # Calculate quick stats
    total_students = Student.objects.filter(is_active=True).count()
    
    # User/Staff statistics - for admin role only
    staff_stats = None
    if request.user.role == 'admin' or request.user.is_superuser:
        staff_stats = {
            'total_users': CustomUser.objects.count(),
            'admin': CustomUser.objects.filter(role='admin').count(),
            'accountant': CustomUser.objects.filter(role='accountant').count(),
            'active_users': CustomUser.objects.filter(is_active=True).count(),
            'inactive_users': CustomUser.objects.filter(is_active=False).count(),
        }
    
    # Billing statistics
    monthly_revenue = Payment.objects.filter(
        status='completed',
        payment_date__month=datetime.now().month,
        payment_date__year=datetime.now().year
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    pending_payments = Invoice.objects.filter(
        status__in=['pending', 'partial', 'overdue']
    ).aggregate(total=Sum('balance_amount'))['total'] or 0
    
    overdue_count = Invoice.objects.filter(status='overdue').count()
    
    # Get user's accessible modules
    user_modules = get_user_modules(request.user)
    
    # Define accountant-only modules
    all_modules = [
        {
            'name': 'Schools & Organization',
            'icon': 'fa-building',
            'description': 'Manage organization and school information',
            'url': '/schools/',
            'color': 'indigo',
            'badge': 'Setup',
            'permission': 'schools'
        },
        {
            'name': 'Student Registry',
            'icon': 'fa-user-graduate',
            'description': 'Minimal student records for billing purposes',
            'url': '/students/',
            'color': 'blue',
            'badge': f'{total_students} Students',
            'permission': 'students'
        },
        {
            'name': 'Simplified Tax Invoice Entry',
            'icon': 'fa-file-invoice',
            'description': 'Quick invoice creation with cash collection',
            'url': '/billing/invoice/create/',
            'color': 'green',
            'badge': 'Create',
            'permission': 'billing'
        },
        {
            'name': 'Tax Invoice Management',
            'icon': 'fa-file-invoice-dollar',
            'description': 'Complete invoice with VAT calculation',
            'url': '/billing/',
            'color': 'emerald',
            'badge': 'VAT 15%',
            'permission': 'billing'
        },
        {
            'name': 'Unpaid Tuition Report',
            'icon': 'fa-exclamation-triangle',
            'description': 'View all pending payments and overdue invoices',
            'url': '/billing/?status=overdue',
            'color': 'red',
            'badge': f'{overdue_count} Overdue',
            'permission': 'billing'
        },
        {
            'name': 'Advanced Accounting',
            'icon': 'fa-calculator',
            'description': 'Double-entry accounting, journal entries & financial reports',
            'url': '/accounting/',
            'color': 'blue',
            'badge': 'General Ledger',
            'permission': 'accounting'
        },
        {
            'name': 'Financial Reports',
            'icon': 'fa-chart-line',
            'description': 'Generate financial reports and statements',
            'url': '/reports/',
            'color': 'purple',
            'badge': 'View',
            'permission': 'reports'
        },
        {
            'name': 'System Configuration',
            'icon': 'fa-cogs',
            'description': 'Configure fees, discounts & VAT settings',
            'url': '/settings/',
            'color': 'gray',
            'badge': 'Configure',
            'permission': 'settings'
        },
        {
            'name': 'Change Password',
            'icon': 'fa-key',
            'description': 'Update your account password securely',
            'url': '/accounts/profile/',
            'color': 'amber',
            'badge': 'Security',
            'permission': 'dashboard'  # Available to all
        },
        {
            'name': 'Exit / Logout',
            'icon': 'fa-sign-out-alt',
            'description': 'Logout from the system safely',
            'url': '/accounts/logout/',
            'color': 'red',
            'badge': 'Exit',
            'permission': 'dashboard'  # Available to all
        },
    ]
    
    # Filter modules based on user role
    if request.user.is_superuser:
        # Superuser sees all modules
        filtered_modules = all_modules
    else:
        # Filter based on role permissions
        filtered_modules = [
            module for module in all_modules 
            if module['permission'] in user_modules or module['permission'] == 'dashboard'
        ]
    
    context = {
        'title': 'Accountant Dashboard',
        'current_year': datetime.now().year,
        'user_role': request.user.get_role_display() if hasattr(request.user, 'role') else 'User',
        
        # Quick Financial Statistics
        'total_students': total_students,
        'monthly_revenue': f'{monthly_revenue:,.2f}',
        'pending_payments': f'{pending_payments:,.2f}',
        'overdue_count': overdue_count,
        
        # Staff/User Statistics (admin only)
        'staff_stats': staff_stats,
        
        # Filtered modules based on role
        'modules': filtered_modules,
    }
    
    return render(request, 'dashboard/index.html', context)


@login_required
@module_required('dashboard')
def system_statistics(request):
    """
    Detailed system statistics view - Admin only
    Shows comprehensive counts of all users and students (Accountant mode)
    """
    from students.models import Student
    from billing.models import Invoice, Payment
    from accounts.models import CustomUser
    from django.db.models import Sum, Count
    
    # Check if user is admin
    if request.user.role not in ['admin'] and not request.user.is_superuser:
        from django.contrib import messages
        from django.shortcuts import redirect
        messages.error(request, 'You do not have permission to view system statistics.')
        return redirect('dashboard:index')
    
    # User/Staff Statistics (Accountant mode - simplified)
    user_stats = {
        'total_users': CustomUser.objects.count(),
        'by_role': {
            'Admin': CustomUser.objects.filter(role='admin').count(),
            'Accountant': CustomUser.objects.filter(role='accountant').count(),
        },
        'by_status': {
            'Active': CustomUser.objects.filter(is_active=True).count(),
            'Inactive': CustomUser.objects.filter(is_active=False).count(),
        },
        'staff_members': CustomUser.objects.filter(is_staff=True).count(),
        'superusers': CustomUser.objects.filter(is_superuser=True).count(),
    }
    
    # Student Statistics (for billing)
    student_stats = {
        'total_students': Student.objects.count(),
        'active_students': Student.objects.filter(is_active=True).count(),
        'inactive_students': Student.objects.filter(is_active=False).count(),
    }
    
    # Financial Statistics
    financial_stats = {
        'total_invoices': Invoice.objects.count(),
        'pending_invoices': Invoice.objects.filter(status='pending').count(),
        'paid_invoices': Invoice.objects.filter(status='paid').count(),
        'overdue_invoices': Invoice.objects.filter(status='overdue').count(),
        'total_revenue': Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0,
        'pending_amount': Invoice.objects.filter(status__in=['pending', 'partial', 'overdue']).aggregate(Sum('balance_amount'))['balance_amount__sum'] or 0,
        'monthly_revenue': Payment.objects.filter(
            status='completed',
            payment_date__month=datetime.now().month,
            payment_date__year=datetime.now().year
        ).aggregate(Sum('amount'))['amount__sum'] or 0,
    }
    
    context = {
        'title': 'Financial Statistics',
        'user_stats': user_stats,
        'student_stats': student_stats,
        'financial_stats': financial_stats,
    }
    
    return render(request, 'dashboard/statistics.html', context)

