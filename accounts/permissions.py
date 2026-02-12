"""
Role-Based Access Control (RBAC) Permission Mapping

Defines which modules and features each role can access.
"""

# Module names mapping to app URLs
MODULES = {
    'dashboard': 'Dashboard Overview',
    'academic': 'Academic Structure',  # NEW: Branch, Curriculum, Level, Grade, Section management
    'students': 'Student Management',
    'enrollment': 'Enrollment Planning',
    'timetable': 'Timetable Management',
    'attendance': 'Attendance Management',  # Teacher core module
    'marks': 'Marks & Exams',  # Teacher core module
    'homework': 'Homework & Notices',  # Teacher core module
    'leave': 'Leave Requests',  # Teacher leave management
    'reports': 'Reports & Analytics',
    'billing': 'Billing & Invoices',
    'accounting': 'Advanced Accounting',  # Double-entry accounting system
    'inventory': 'Inventory Management',
    'maintenance': 'Maintenance Requests',
    'workflow': 'Workflow & Approvals',
    'settings': 'System Settings',
}

# Role-based permission mapping
ROLE_PERMISSIONS = {
    'admin': [
        # Admin has full access to all modules
        'dashboard',
        'academic',    # FULL: Manage all hierarchy levels
        'students',
        'enrollment',
        'timetable',
        'attendance',  # Full attendance access
        'marks',       # Full marks and exams access
        'homework',    # Full homework access
        'leave',       # Full leave management access
        'billing',
        'accounting',  # FULL: Advanced accounting system
        'reports',
        'inventory',
        'maintenance',
        'workflow',
        'settings',
    ],
    'teacher': [
        # Teacher: student info, timetable, attendance, marks, homework, reports, leave
        # FILTERED by assigned curriculum/level/grade/section
        # NO ACCESS to billing/financial/inventory/workflow/settings
        'dashboard',
        'students',    # View only (read-only student registry) - FILTERED by assignment
        'timetable',   # View class schedule - FILTERED by assignment
        'attendance',  # Daily attendance marking (CORE) - FILTERED by assignment
        'marks',       # Enter/edit exam marks (CORE) - FILTERED by assignment
        'homework',    # Homework & class notices (CORE) - FILTERED by assignment
        'reports',     # Student academic reports only (NOT financial) - FILTERED
        'leave',       # Leave requests (apply/view own)
    ],
    'staff': [
        # Staff: student registry, enrollment planning, inventory, maintenance
        'dashboard',
        'students',
        'enrollment',
        'inventory',
        'maintenance',
    ],
    'accountant': [
        # Accountant: invoices, tax, unpaid tuition, sales reports, accounting
        'dashboard',
        'billing',
        'accounting',  # Advanced accounting (journal entries, ledgers, financial reports)
        'reports',  # Financial reports
    ],
    'hr': [
        # HR: workflow approvals, staff records (no student/fees)
        'dashboard',
        'workflow',
        'settings',  # HR-related settings only
    ],
}

# Granular permissions for specific actions within modules
MODULE_ACTIONS = {
    'students': {
        'view': ['admin', 'teacher', 'staff'],
        'create': ['admin', 'staff'],
        'edit': ['admin', 'staff'],
        'delete': ['admin'],
        'export': ['admin', 'teacher', 'staff'],
    },
    'attendance': {
        'view': ['admin', 'teacher'],
        'mark': ['admin', 'teacher'],  # Daily attendance marking
        'edit': ['admin', 'teacher'],  # Edit attendance (same day only)
        'history': ['admin', 'teacher'],  # Class-wise attendance history
        'report': ['admin'],  # Attendance reports
    },
    'marks': {
        'view': ['admin', 'teacher'],
        'enter': ['admin', 'teacher'],  # Enter exam/test marks
        'edit': ['admin', 'teacher'],  # Edit marks (limited time window)
        'delete': ['admin'],  # Only admin can delete marks
        'class_performance': ['admin', 'teacher'],  # View class performance
    },
    'homework': {
        'view': ['admin', 'teacher'],
        'create': ['admin', 'teacher'],  # Upload homework assignments
        'edit': ['admin', 'teacher'],  # Edit homework
        'delete': ['admin', 'teacher'],  # Delete homework
        'notice': ['admin', 'teacher'],  # Post class notices
    },
    'leave': {
        'view': ['admin', 'teacher', 'staff', 'hr'],  # View own leave requests
        'create': ['admin', 'teacher', 'staff'],  # Apply for leave
        'edit': ['admin', 'teacher', 'staff'],  # Edit pending leave requests
        'approve': ['admin', 'hr'],  # Approve/reject leave
        'view_all': ['admin', 'hr'],  # View all leave requests
    },
    'billing': {
        'view': ['admin', 'accountant'],
        'create': ['admin', 'accountant'],
        'edit': ['admin', 'accountant'],
        'delete': ['admin'],
        'generate_pdf': ['admin', 'accountant'],
    },
    'accounting': {
        'view': ['admin', 'accountant'],  # View accounting dashboard and reports
        'view_accounts': ['admin', 'accountant'],  # View chart of accounts
        'create_account': ['admin', 'accountant'],  # Create new accounts
        'edit_account': ['admin', 'accountant'],  # Edit accounts
        'setup_accounts': ['admin'],  # Setup default chart of accounts (admin only)
        'view_journal': ['admin', 'accountant'],  # View journal entries
        'create_journal': ['admin', 'accountant'],  # Create journal entries
        'edit_journal': ['admin', 'accountant'],  # Edit draft journal entries
        'post_journal': ['admin'],  # Post journal entries (admin only)
        'view_reports': ['admin', 'accountant'],  # View financial reports
        'manage_fiscal_year': ['admin'],  # Create/edit fiscal years (admin only)
    },
    'reports': {
        'view': ['admin', 'accountant'],  # Financial reports
        'create': ['admin'],
        'export': ['admin', 'accountant'],
        'financial': ['admin', 'accountant'],  # Financial/sales reports (admin & accountant only)
        'student_academic': ['admin', 'teacher'],  # Academic/performance reports (admin & teacher)
        'attendance_report': ['admin', 'teacher'],  # Attendance reports
        'marks_report': ['admin', 'teacher'],  # Marks/exam reports
    },
    'enrollment': {
        'view': ['admin', 'staff'],
        'create': ['admin', 'staff'],
        'edit': ['admin', 'staff'],
        'approve': ['admin'],
    },
    'timetable': {
        'view': ['admin', 'teacher', 'staff'],
        'create': ['admin'],
        'edit': ['admin'],
    },
    'inventory': {
        'view': ['admin', 'staff'],
        'create': ['admin', 'staff'],
        'edit': ['admin', 'staff'],
        'delete': ['admin'],
    },
    'maintenance': {
        'view': ['admin', 'staff'],
        'create': ['admin', 'staff'],
        'edit': ['admin', 'staff'],
        'resolve': ['admin'],
    },
    'workflow': {
        'view': ['admin', 'hr'],
        'approve': ['admin', 'hr'],
        'reject': ['admin', 'hr'],
    },
    'settings': {
        'view': ['admin', 'hr'],
        'edit': ['admin'],
    },
}


def has_module_permission(user, module_name):
    """
    Check if user has permission to access a module
    
    Args:
        user: CustomUser instance
        module_name: String name of the module
        
    Returns:
        Boolean indicating if user has access
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    return module_name in ROLE_PERMISSIONS.get(user.role, [])


def has_action_permission(user, module_name, action):
    """
    Check if user has permission for a specific action within a module
    
    Args:
        user: CustomUser instance
        module_name: String name of the module
        action: String action name (view, create, edit, delete, etc.)
        
    Returns:
        Boolean indicating if user has permission for the action
    """
    if not user.is_authenticated:
        return False
    
    if user.is_superuser:
        return True
    
    # Check if module exists and has action permissions defined
    if module_name not in MODULE_ACTIONS:
        # If no granular permissions defined, fall back to module permission
        return has_module_permission(user, module_name)
    
    # Check if action is defined for the module
    if action not in MODULE_ACTIONS[module_name]:
        return False
    
    # Check if user's role is in the allowed roles for this action
    return user.role in MODULE_ACTIONS[module_name][action]


def get_user_modules(user):
    """
    Get list of modules accessible to the user
    
    Args:
        user: CustomUser instance
        
    Returns:
        List of module names the user can access
    """
    if not user.is_authenticated:
        return []
    
    if user.is_superuser:
        return list(MODULES.keys())
    
    return ROLE_PERMISSIONS.get(user.role, [])


def get_role_display_name(role):
    """
    Get human-readable display name for a role
    
    Args:
        role: String role code
        
    Returns:
        String display name
    """
    role_names = {
        'admin': 'Administrator',
        'teacher': 'Teacher',
        'staff': 'Staff Member',
        'accountant': 'Accountant',
        'hr': 'Human Resources',
    }
    return role_names.get(role, role.title())


# ======================================================
# ACADEMIC HIERARCHY RBAC FUNCTIONS (NEW)
# ======================================================
# NOTE: Teacher-specific functions commented out (accountant-only mode)

# def get_teacher_assignments(user):
#     """Get all academic assignments for a teacher"""
#     return None

# def get_teacher_sections(user):
#     """Get all sections assigned to a teacher"""
#     return None

# def get_teacher_grades(user):
#     """Get all grades assigned to a teacher"""
#     return None

def get_teacher_students(user):
    """
    Get all students assigned to a teacher (simplified for accountant mode)
    """
    if user.role == 'admin' or user.role == 'accountant':
        from students.models import Student
        return Student.objects.filter(is_active=True)
    return None


def can_teacher_access_section(user, section):
    """Check if teacher has access to a specific section (simplified)"""
    if user.role == 'admin' or user.role == 'accountant':
        return True
    return False


def can_teacher_access_student(user, student):
    """Check if teacher has access to a specific student (simplified)"""
    if user.role == 'admin' or user.role == 'accountant':
        return True
    return False
