from django.urls import path
from . import views

app_name = 'settings_app'

urlpatterns = [
    # Settings Dashboard
    path('', views.settings_dashboard, name='dashboard'),
    
    # School Year URLs
    path('school-years/', views.school_year_list, name='school_year_list'),
    path('school-years/create/', views.school_year_create, name='school_year_create'),
    path('school-years/<int:pk>/edit/', views.school_year_edit, name='school_year_edit'),
    path('school-years/<int:pk>/delete/', views.school_year_delete, name='school_year_delete'),
    
    # Program URLs
    path('programs/', views.program_list, name='program_list'),
    path('programs/create/', views.program_create, name='program_create'),
    path('programs/<int:pk>/edit/', views.program_edit, name='program_edit'),
    
    # Grade URLs
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/', views.grade_create, name='grade_create'),
    path('grades/<int:pk>/edit/', views.grade_edit, name='grade_edit'),
    
    # Section URLs
    path('sections/', views.section_list, name='section_list'),
    path('sections/create/', views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/', views.section_edit, name='section_edit'),
    
    # Fee Structure URLs
    path('fee-structures/', views.fee_structure_list, name='fee_structure_list'),
    path('fee-structures/create/', views.fee_structure_create, name='fee_structure_create'),
    path('fee-structures/<int:pk>/edit/', views.fee_structure_edit, name='fee_structure_edit'),
    
    # VAT Config URLs
    path('vat-config/', views.vat_config_list, name='vat_config_list'),
    path('vat-config/create/', views.vat_config_create, name='vat_config_create'),
    path('vat-config/<int:pk>/edit/', views.vat_config_edit, name='vat_config_edit'),
]
