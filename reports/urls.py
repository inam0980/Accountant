from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Dashboard
    path('', views.reports_dashboard, name='dashboard'),
    
    # Report Types
    path('student/', views.student_report, name='student_report'),
    path('financial/', views.financial_report, name='financial_report'),
    path('fee-collection/', views.fee_collection_report, name='fee_collection'),
    path('outstanding/', views.outstanding_fees_report, name='outstanding_fees'),
    
    # Export
    path('export/<str:report_type>/', views.export_report, name='export_report'),
    
    # Saved Reports
    path('saved/', views.saved_reports_list, name='saved_reports'),
    path('saved/<int:report_id>/', views.view_saved_report, name='view_saved_report'),
    path('save/', views.save_report, name='save_report'),
]
