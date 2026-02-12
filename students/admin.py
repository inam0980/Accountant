from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'first_name', 'last_name', 'email', 'phone', 'is_active']
    list_filter = ['is_active', 'school']
    search_fields = ['student_id', 'first_name', 'last_name', 'email']
    ordering = ['student_id']
