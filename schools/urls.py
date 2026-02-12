from django.urls import path
from . import views

app_name = 'schools'

urlpatterns = [
    # Organization URLs
    path('organizations/', views.organization_dashboard, name='organization_dashboard'),
    path('organizations/list/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('organizations/<int:pk>/update/', views.organization_update, name='organization_update'),
    
    # School URLs
    path('', views.school_dashboard, name='school_dashboard'),
    path('list/', views.school_list, name='school_list'),
    path('create/', views.school_create, name='school_create'),
    path('<int:pk>/', views.school_detail, name='school_detail'),
    path('<int:pk>/update/', views.school_update, name='school_update'),
    path('<int:pk>/switch/', views.school_switch, name='school_switch'),
    
    # Academic Configuration
    path('<int:school_pk>/academic-config/', views.academic_config_update, name='academic_config_update'),
    
    # Branding
    path('<int:school_pk>/branding/', views.branding_update, name='branding_update'),
    
    # School Admin
    path('<int:school_pk>/admin/create/', views.school_admin_create, name='school_admin_create'),
    path('admin/<int:pk>/update/', views.school_admin_update, name='school_admin_update'),
]
