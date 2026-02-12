from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class Organization(models.Model):
    """
    Top-level entity representing the educational organization/group.
    Can manage multiple schools under one umbrella.
    """
    name = models.CharField(max_length=200, unique=True)
    name_arabic = models.CharField(max_length=200, blank=True, null=True)
    registration_number = models.CharField(max_length=100, unique=True)
    organization_code = models.CharField(max_length=50, unique=True)
    
    # Commercial Registration (CR) Number - Required for Saudi receipts
    cr_number = models.CharField(max_length=50, blank=True, verbose_name="CR Number (Commercial Registration)")
    
    # Contact Information
    email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)
    mobile = models.CharField(max_length=15, blank=True, verbose_name="Mobile Number")
    website = models.URLField(blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default='Saudi Arabia')
    
    # Logo and Branding
    logo = models.ImageField(upload_to='organization/logos/', blank=True, null=True)
    
    # Tax Information (for ZATCA compliance)
    tax_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="Tax Number")
    vat_registration_number = models.CharField(max_length=50, blank=True, null=True, verbose_name="VAT Registration Number")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name
    
    @property
    def total_schools(self):
        """Return total number of schools under this organization"""
        return self.schools.filter(is_active=True).count()
    
    @property
    def total_students(self):
        """Return total number of students across all schools"""
        from students.models import Student
        return Student.objects.filter(school__organization=self, is_active=True).count()


class School(models.Model):
    """
    Individual school/branch within an organization.
    Each school operates semi-independently with its own configuration.
    """
    SCHOOL_TYPE_CHOICES = [
        ('boys', 'Boys School'),
        ('girls', 'Girls School'),
        ('mixed', 'Co-education'),
    ]
    
    SHIFT_CHOICES = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('full_day', 'Full Day'),
    ]
    
    # Basic Information
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='schools')
    school_name = models.CharField(max_length=200)
    school_name_arabic = models.CharField(max_length=200, blank=True, null=True)
    school_code = models.CharField(max_length=50, unique=True)
    school_type = models.CharField(max_length=20, choices=SCHOOL_TYPE_CHOICES, default='mixed')
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default='morning')
    
    # Contact Information
    email = models.EmailField()
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(validators=[phone_regex], max_length=15)
    mobile = models.CharField(max_length=15, blank=True, verbose_name="Mobile Number")
    fax = models.CharField(max_length=20, blank=True, null=True)
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    
    # License & Accreditation
    license_number = models.CharField(max_length=100, blank=True, null=True)
    accreditation_body = models.CharField(max_length=200, blank=True, null=True)
    accreditation_number = models.CharField(max_length=100, blank=True, null=True)
    establishment_date = models.DateField(blank=True, null=True)
    
    # Principal/Director Information
    principal_name = models.CharField(max_length=200)
    principal_email = models.EmailField()
    principal_phone = models.CharField(validators=[phone_regex], max_length=15)
    
    # Capacity
    total_capacity = models.PositiveIntegerField(default=0, help_text="Maximum student capacity")
    
    # Logo and Branding
    logo = models.ImageField(upload_to='schools/logos/', blank=True, null=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['organization', 'school_name']
        unique_together = ['organization', 'school_code']
    
    def __str__(self):
        return f"{self.school_name} ({self.school_code})"
    
    @property
    def current_enrollment(self):
        """Return current number of enrolled students"""
        from students.models import Student
        return Student.objects.filter(school=self, is_active=True).count()
    
    @property
    def available_capacity(self):
        """Return available seats"""
        return max(0, self.total_capacity - self.current_enrollment)
    
    @property
    def enrollment_percentage(self):
        """Return enrollment percentage"""
        if self.total_capacity > 0:
            return round((self.current_enrollment / self.total_capacity) * 100, 2)
        return 0


class AcademicConfig(models.Model):
    """
    School-specific academic configuration settings.
    Each school can have different academic calendars, terms, etc.
    """
    GRADING_SYSTEM_CHOICES = [
        ('percentage', 'Percentage (0-100)'),
        ('gpa_4', 'GPA 4.0 Scale'),
        ('gpa_5', 'GPA 5.0 Scale'),
        ('letter', 'Letter Grades (A-F)'),
        ('custom', 'Custom System'),
    ]
    
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='academic_config')
    
    # Academic Year
    current_academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    academic_year_start = models.DateField()
    academic_year_end = models.DateField()
    
    # Term/Semester Configuration
    number_of_terms = models.PositiveIntegerField(
        default=2,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        help_text="Number of terms/semesters per academic year"
    )
    
    # Working Days
    working_days = models.CharField(
        max_length=50,
        default='sunday,monday,tuesday,wednesday,thursday',
        help_text="Comma-separated working days"
    )
    
    # Class Timing
    class_start_time = models.TimeField(default='07:30:00')
    class_end_time = models.TimeField(default='14:00:00')
    class_duration = models.PositiveIntegerField(default=45, help_text="Class duration in minutes")
    break_duration = models.PositiveIntegerField(default=10, help_text="Break duration in minutes")
    
    # Grading System
    grading_system = models.CharField(max_length=20, choices=GRADING_SYSTEM_CHOICES, default='percentage')
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=50.00)
    
    # Attendance Requirements
    minimum_attendance_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=75.00,
        help_text="Minimum attendance required for promotion"
    )
    
    # Promotion Rules
    auto_promotion_enabled = models.BooleanField(default=False)
    promotion_criteria = models.TextField(
        blank=True,
        null=True,
        help_text="Custom promotion criteria/rules"
    )
    
    # Late Arrival Policy
    late_arrival_grace_period = models.PositiveIntegerField(
        default=15,
        help_text="Grace period in minutes before marking late"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Academic Configuration'
        verbose_name_plural = 'Academic Configurations'
    
    def __str__(self):
        return f"Academic Config - {self.school.school_name}"


class SchoolBranding(models.Model):
    """
    School-specific branding and customization settings.
    Allows each school to have unique visual identity.
    """
    school = models.OneToOneField(School, on_delete=models.CASCADE, related_name='branding')
    
    # Colors
    primary_color = models.CharField(max_length=7, default='#1e40af', help_text="Hex color code")
    secondary_color = models.CharField(max_length=7, default='#059669', help_text="Hex color code")
    accent_color = models.CharField(max_length=7, default='#dc2626', help_text="Hex color code")
    
    # Images
    header_logo = models.ImageField(upload_to='schools/branding/headers/', blank=True, null=True)
    footer_logo = models.ImageField(upload_to='schools/branding/footers/', blank=True, null=True)
    favicon = models.ImageField(upload_to='schools/branding/favicons/', blank=True, null=True)
    background_image = models.ImageField(upload_to='schools/branding/backgrounds/', blank=True, null=True)
    
    # Text Content
    tagline = models.CharField(max_length=200, blank=True, null=True)
    tagline_arabic = models.CharField(max_length=200, blank=True, null=True)
    vision_statement = models.TextField(blank=True, null=True)
    mission_statement = models.TextField(blank=True, null=True)
    
    # Social Media
    facebook_url = models.URLField(blank=True, null=True)
    twitter_url = models.URLField(blank=True, null=True)
    instagram_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    
    # Report Headers/Footers
    report_header_text = models.TextField(blank=True, null=True)
    report_footer_text = models.TextField(blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'School Branding'
        verbose_name_plural = 'School Branding'
    
    def __str__(self):
        return f"Branding - {self.school.school_name}"


class SchoolAdmin(models.Model):
    """
    School administrators with specific permissions.
    Allows delegation of school management to specific users.
    """
    ROLE_CHOICES = [
        ('principal', 'Principal'),
        ('vice_principal', 'Vice Principal'),
        ('academic_director', 'Academic Director'),
        ('admin_officer', 'Administrative Officer'),
        ('registrar', 'Registrar'),
        ('coordinator', 'Coordinator'),
    ]
    
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='administrators')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='school_admin_roles')
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    
    # Permissions
    can_manage_students = models.BooleanField(default=False)
    can_manage_teachers = models.BooleanField(default=False)
    can_manage_curriculum = models.BooleanField(default=False)
    can_manage_fees = models.BooleanField(default=False)
    can_view_reports = models.BooleanField(default=True)
    can_manage_timetable = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    assigned_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ['school', 'user', 'role']
        ordering = ['school', 'role']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_role_display()} at {self.school.school_name}"
