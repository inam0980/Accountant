"""
Context processors for accounting module
Makes permissions available in templates
"""

from accounts.permissions import has_action_permission


def accounting_permissions(request):
    """
    Add accounting permissions to template context
    """
    if not request.user.is_authenticated:
        return {}
    
    return {
        'can_create_account': has_action_permission(request.user, 'accounting', 'create_account'),
        'can_edit_account': has_action_permission(request.user, 'accounting', 'edit_account'),
        'can_setup_accounts': has_action_permission(request.user, 'accounting', 'setup_accounts'),
        'can_create_journal': has_action_permission(request.user, 'accounting', 'create_journal'),
        'can_edit_journal': has_action_permission(request.user, 'accounting', 'edit_journal'),
        'can_post_journal': has_action_permission(request.user, 'accounting', 'post_journal'),
        'can_view_reports': has_action_permission(request.user, 'accounting', 'view_reports'),
        'can_manage_fiscal_year': has_action_permission(request.user, 'accounting', 'manage_fiscal_year'),
    }
