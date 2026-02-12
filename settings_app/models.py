from django.db import models
from django.core.exceptions import ValidationError

# Create your models here.

class SchoolYear(models.Model):
    """
    Academic Year/School Year Configuration
    """
    name = models.CharField(max_length=20, unique=True, help_text="e.g., 2025-2026")
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False, help_text="Only one year can be active at a time")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
        verbose_name = 'School Year'
        verbose_name_plural = 'School Years'
    
    def __str__(self):
        return f"{self.name} {'(Active)' if self.is_active else ''}"
    
    def clean(self):
        # Ensure only one active school year
        if self.is_active:
            active_years = SchoolYear.objects.filter(is_active=True).exclude(pk=self.pk)
            if active_years.exists():
                raise ValidationError('Only one school year can be active at a time. Please deactivate the current active year first.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Program(models.Model):
    """
    Educational Programs (Elementary, Middle School, High School)
    """
    name = models.CharField(max_length=100, unique=True, help_text="e.g., Elementary School")
    code = models.CharField(max_length=10, unique=True, help_text="e.g., ELEM")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'
    
    def __str__(self):
        return self.name


class Grade(models.Model):
    """
    Grade/Class Levels
    """
    name = models.CharField(max_length=50, help_text="e.g., Grade 1, Grade 2")
    code = models.CharField(max_length=10, help_text="e.g., G1, G2")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='grades')
    order = models.IntegerField(default=0, help_text="Display order")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['program', 'order']
        unique_together = ['program', 'code']
        verbose_name = 'Grade/Class'
        verbose_name_plural = 'Grades/Classes'
    
    def __str__(self):
        return f"{self.program.name} - {self.name}"


class Section(models.Model):
    """
    Section/Division within a Grade
    """
    name = models.CharField(max_length=10, help_text="e.g., A, B, C")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='sections')
    capacity = models.IntegerField(default=30, help_text="Maximum number of students")
    current_strength = models.IntegerField(default=0, help_text="Current number of students")
    class_teacher = models.CharField(max_length=200, blank=True, help_text="Class teacher name")
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['grade', 'name']
        unique_together = ['grade', 'name']
        verbose_name = 'Section'
        verbose_name_plural = 'Sections'
    
    def __str__(self):
        return f"{self.grade.name} - Section {self.name}"
    
    def is_full(self):
        return self.current_strength >= self.capacity


class FeeStructure(models.Model):
    """
    Fee Structure Configuration
    """
    FEE_TYPE_CHOICES = [
        ('Tuition', 'Tuition Fee'),
        ('Transport', 'Transport Fee'),
        ('Books', 'Books & Materials'),
        ('Uniform', 'Uniform'),
        ('Activities', 'Extracurricular Activities'),
        ('Registration', 'Registration Fee'),
        ('Examination', 'Examination Fee'),
        ('Other', 'Other Fees'),
    ]
    
    PAYMENT_SCHEDULE_CHOICES = [
        ('Annual', 'Annual (Once per year)'),
        ('Semester', 'Semester (Twice per year)'),
        ('Quarterly', 'Quarterly (4 times per year)'),
        ('Monthly', 'Monthly'),
        ('One-time', 'One-time Payment'),
    ]
    
    name = models.CharField(max_length=200, help_text="e.g., Regular Tuition - Grade 1")
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='fee_structures')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='fee_structures')
    
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in SAR")
    payment_schedule = models.CharField(max_length=20, choices=PAYMENT_SCHEDULE_CHOICES)
    
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['program', 'grade', 'fee_type']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'
    
    def __str__(self):
        return f"{self.name} - {self.amount} SAR ({self.payment_schedule})"


class VATConfig(models.Model):
    """
    VAT Configuration Settings
    """
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=15.00, help_text="VAT percentage (e.g., 15 for 15%)")
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True, help_text="Leave blank if still active")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, help_text="Notes about this VAT configuration")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-effective_from']
        verbose_name = 'VAT Configuration'
        verbose_name_plural = 'VAT Configurations'
    
    def __str__(self):
        return f"VAT {self.vat_percentage}% (Effective from {self.effective_from})"
    
    def clean(self):
        # Ensure only one active VAT config
        if self.is_active:
            active_configs = VATConfig.objects.filter(is_active=True).exclude(pk=self.pk)
            if active_configs.exists():
                raise ValidationError('Only one VAT configuration can be active at a time.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

