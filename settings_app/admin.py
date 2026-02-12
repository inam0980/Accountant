from django.contrib import admin
from .models import SchoolYear, Program, Grade, Section, FeeStructure, VATConfig

# Register your models here.

@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    ordering = ['-start_date']

@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'code']

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'program', 'order', 'is_active']
    list_filter = ['program', 'is_active']
    search_fields = ['name', 'code']
    ordering = ['program', 'order']

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'grade', 'capacity', 'current_strength', 'class_teacher', 'is_active']
    list_filter = ['grade__program', 'grade', 'is_active']
    search_fields = ['name', 'class_teacher']

@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ['name', 'program', 'grade', 'fee_type', 'amount', 'payment_schedule', 'is_active']
    list_filter = ['program', 'grade', 'fee_type', 'payment_schedule', 'is_active']
    search_fields = ['name']

@admin.register(VATConfig)
class VATConfigAdmin(admin.ModelAdmin):
    list_display = ['vat_percentage', 'effective_from', 'effective_to', 'is_active']
    list_filter = ['is_active']
    ordering = ['-effective_from']
