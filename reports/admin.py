from django.contrib import admin
from .models import ReportTemplate, SavedReport, ScheduledReport


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'report_type', 'is_active', 'created_by', 'created_at']
    list_filter = ['report_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    date_hierarchy = 'created_at'


@admin.register(SavedReport)
class SavedReportAdmin(admin.ModelAdmin):
    list_display = ['title', 'report_type', 'generated_by', 'generated_at', 'total_records']
    list_filter = ['report_type', 'generated_at', 'is_scheduled']
    search_fields = ['title', 'notes']
    date_hierarchy = 'generated_at'
    readonly_fields = ['generated_at', 'data', 'summary_data']


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'frequency', 'is_active', 'next_run', 'last_run']
    list_filter = ['frequency', 'is_active']
    search_fields = ['name', 'email_recipients']
    date_hierarchy = 'next_run'
