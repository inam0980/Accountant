from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom User model with role-based access control
    Extends Django's AbstractUser to add role field
    """
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('accountant', 'Accountant'),
        ('hr', 'HR'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='staff',
        help_text='User role determines access permissions'
    )
    
    employee_id = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        help_text='Employee/Staff ID for identification'
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text='Contact phone number'
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text='Department or subject area'
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text='Designates whether this user should be treated as active'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    def get_dashboard_url(self):
        """
        Returns the appropriate dashboard URL based on user role
        """
        return '/'  # All roles use the same dashboard with filtered cards
    
    def has_module_access(self, module_name):
        """
        Check if user's role has access to a specific module
        """
        from .permissions import ROLE_PERMISSIONS
        return module_name in ROLE_PERMISSIONS.get(self.role, [])
    
    def get_accessible_modules(self):
        """
        Get list of modules this user can access based on role
        """
        from .permissions import ROLE_PERMISSIONS
        return ROLE_PERMISSIONS.get(self.role, [])
