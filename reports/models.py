from django.db import models
from django.conf import settings
from django.utils import timezone
from students.models import Student
from billing.models import Invoice

class ReportTemplate(models.Model):
    """Pre-defined report templates"""
    REPORT_TYPES = [
        ('student', 'Student Report'),
        ('financial', 'Financial Report'),
        ('attendance', 'Attendance Report'),
        ('enrollment', 'Enrollment Report'),
        ('fee_collection', 'Fee Collection Report'),
        ('outstanding', 'Outstanding Fees Report'),
        ('performance', 'Academic Performance Report'),
        ('class_wise', 'Class-wise Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"


class SavedReport(models.Model):
    """Saved/Generated reports for future reference"""
    template = models.ForeignKey(ReportTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    report_type = models.CharField(max_length=50, choices=ReportTemplate.REPORT_TYPES)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Date range for the report
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)
    
    # Filters used
    student_filter = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Report data (stored as JSON)
    data = models.JSONField(default=dict)
    
    # Summary statistics
    total_records = models.IntegerField(default=0)
    summary_data = models.JSONField(default=dict)
    
    # Export paths
    pdf_path = models.CharField(max_length=500, blank=True)
    excel_path = models.CharField(max_length=500, blank=True)
    
    notes = models.TextField(blank=True)
    is_scheduled = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['-generated_at']),
            models.Index(fields=['report_type']),
        ]
        
    def __str__(self):
        return f"{self.title} - {self.generated_at.strftime('%Y-%m-%d')}"


class ScheduledReport(models.Model):
    """Scheduled reports to be generated automatically"""
    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    template = models.ForeignKey(ReportTemplate, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    is_active = models.BooleanField(default=True)
    
    # Recipients
    email_recipients = models.TextField(help_text="Comma-separated email addresses")
    
    # Schedule
    next_run = models.DateTimeField()
    last_run = models.DateTimeField(null=True, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['next_run']
        
    def __str__(self):
        return f"{self.name} ({self.frequency})"
