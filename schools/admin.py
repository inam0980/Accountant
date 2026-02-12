from django.contrib import admin
from .models import Organization, School, AcademicConfig, SchoolBranding, SchoolAdmin as SchoolAdminModel


class SchoolInline(admin.TabularInline):
    """Inline for managing schools within organization"""
    model = School
    extra = 0
    fields = ['school_name', 'school_code', 'school_type', 'principal_name', 'is_active']
    show_change_link = True


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin configuration for Organization model"""
    list_display = ['name', 'organization_code', 'city', 'country', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active', 'country', 'created_at']
    search_fields = ['name', 'organization_code', 'registration_number', 'email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [SchoolInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'name_arabic', 'registration_number', 'organization_code')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website')
        }),
        ('Location', {
            'fields': ('address', 'city', 'country')
        }),
        ('Branding', {
            'fields': ('logo',)
        }),
        ('Tax Information', {
            'fields': ('tax_number', 'vat_registration_number')
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


class AcademicConfigInline(admin.StackedInline):
    """Inline for academic configuration"""
    model = AcademicConfig
    can_delete = False
    verbose_name_plural = 'Academic Configuration'


class SchoolBrandingInline(admin.StackedInline):
    """Inline for school branding"""
    model = SchoolBranding
    can_delete = False
    verbose_name_plural = 'Branding Configuration'


class SchoolAdminInline(admin.TabularInline):
    """Inline for school administrators"""
    model = SchoolAdminModel
    extra = 0
    fields = ['user', 'role', 'is_active']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    """Admin configuration for School model"""
    list_display = [
        'school_name', 'school_code', 'organization', 'school_type',
        'shift', 'principal_name', 'total_capacity', 'is_active'
    ]
    list_filter = ['is_active', 'school_type', 'shift', 'organization', 'created_at']
    search_fields = ['school_name', 'school_code', 'principal_name', 'email']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [AcademicConfigInline, SchoolBrandingInline, SchoolAdminInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('organization', 'school_name', 'school_name_arabic', 'school_code', 'school_type', 'shift')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'fax')
        }),
        ('Location', {
            'fields': ('address', 'city', 'district', 'postal_code')
        }),
        ('License & Accreditation', {
            'fields': ('license_number', 'accreditation_body', 'accreditation_number', 'establishment_date')
        }),
        ('Principal Information', {
            'fields': ('principal_name', 'principal_email', 'principal_phone')
        }),
        ('Capacity', {
            'fields': ('total_capacity',)
        }),
        ('Branding', {
            'fields': ('logo',)
        }),
        ('Status', {
            'fields': ('is_active', 'created_at', 'updated_at')
        }),
    )


@admin.register(AcademicConfig)
class AcademicConfigAdmin(admin.ModelAdmin):
    """Admin configuration for AcademicConfig model"""
    list_display = [
        'school', 'current_academic_year', 'number_of_terms',
        'grading_system', 'passing_marks', 'updated_at'
    ]
    list_filter = ['grading_system', 'number_of_terms', 'auto_promotion_enabled']
    search_fields = ['school__school_name', 'current_academic_year']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('School', {
            'fields': ('school',)
        }),
        ('Academic Year', {
            'fields': ('current_academic_year', 'academic_year_start', 'academic_year_end', 'number_of_terms')
        }),
        ('Schedule', {
            'fields': ('working_days', 'class_start_time', 'class_end_time', 'class_duration', 'break_duration')
        }),
        ('Grading & Promotion', {
            'fields': ('grading_system', 'passing_marks', 'auto_promotion_enabled', 'promotion_criteria')
        }),
        ('Attendance', {
            'fields': ('minimum_attendance_percentage', 'late_arrival_grace_period')
        }),
        ('Last Updated', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(SchoolBranding)
class SchoolBrandingAdmin(admin.ModelAdmin):
    """Admin configuration for SchoolBranding model"""
    list_display = ['school', 'primary_color', 'secondary_color', 'accent_color', 'updated_at']
    search_fields = ['school__school_name']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('School', {
            'fields': ('school',)
        }),
        ('Colors', {
            'fields': ('primary_color', 'secondary_color', 'accent_color')
        }),
        ('Images', {
            'fields': ('header_logo', 'footer_logo', 'favicon', 'background_image')
        }),
        ('Text Content', {
            'fields': ('tagline', 'tagline_arabic', 'vision_statement', 'mission_statement')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url')
        }),
        ('Reports', {
            'fields': ('report_header_text', 'report_footer_text')
        }),
        ('Last Updated', {
            'fields': ('updated_at',)
        }),
    )


@admin.register(SchoolAdminModel)
class SchoolAdminModelAdmin(admin.ModelAdmin):
    """Admin configuration for SchoolAdmin model (renamed to avoid conflict)"""
    list_display = ['user', 'school', 'role', 'is_active', 'assigned_date']
    list_filter = ['role', 'is_active', 'school', 'assigned_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'school__school_name']
    date_hierarchy = 'assigned_date'
    
    fieldsets = (
        ('Assignment', {
            'fields': ('school', 'user', 'role')
        }),
        ('Permissions', {
            'fields': (
                'can_manage_students', 'can_manage_teachers', 'can_manage_curriculum',
                'can_manage_fees', 'can_view_reports', 'can_manage_timetable'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'assigned_date', 'notes')
        }),
    )

