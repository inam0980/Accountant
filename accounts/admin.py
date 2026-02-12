from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin interface for CustomUser model - Complete Profile Management
    """
    list_display = ['username', 'get_full_name_display', 'email', 'role', 'employee_id', 'department', 'phone', 'is_active', 'is_staff', 'date_joined']
    list_filter = ['role', 'is_active', 'is_staff', 'is_superuser', 'department', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id', 'department', 'phone']
    ordering = ['-date_joined']
    list_per_page = 50
    actions = ['activate_users', 'deactivate_users', 'make_staff', 'remove_staff']
    date_hierarchy = 'date_joined'
    
    fieldsets = (
        (None, {
            'fields': ('username', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'employee_id', 'department')
        }),
        ('Role & Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('wide',),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone', 'employee_id', 'department'),
        }),
        ('Role & Permissions', {
            'classes': ('wide',),
            'fields': ('role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login', 'date_joined']
    
    def get_full_name_display(self, obj):
        """Display full name with username"""
        full_name = obj.get_full_name()
        if full_name:
            return f"{full_name} ({obj.username})"
        return obj.username
    get_full_name_display.short_description = 'Full Name'
    
    def activate_users(self, request, queryset):
        """Activate selected users"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated successfully.')
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated successfully.')
    deactivate_users.short_description = 'Deactivate selected users'
    
    def make_staff(self, request, queryset):
        """Make selected users staff"""
        updated = queryset.update(is_staff=True)
        self.message_user(request, f'{updated} user(s) made staff successfully.')
    make_staff.short_description = 'Grant staff status'
    
    def remove_staff(self, request, queryset):
        """Remove staff status from selected users"""
        updated = queryset.filter(is_superuser=False).update(is_staff=False)
        self.message_user(request, f'{updated} user(s) removed from staff.')
    remove_staff.short_description = 'Remove staff status'
    
    def get_queryset(self, request):
        """
        Filter queryset based on user role
        Admin can see all users, HR can see non-admin users
        """
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role == 'admin':
            return qs
        if request.user.role == 'hr':
            return qs.exclude(role='admin')
        return qs.filter(id=request.user.id)
