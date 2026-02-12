from django.urls import path
from . import views

app_name = 'accounting'

urlpatterns = [
    # Dashboard
    path('', views.accounting_dashboard, name='dashboard'),
    
    # Chart of Accounts
    path('accounts/', views.chart_of_accounts, name='chart_of_accounts'),
    path('accounts/create/', views.account_create, name='account_create'),
    path('accounts/setup/', views.setup_chart_of_accounts, name='setup_chart_of_accounts'),
    
    # Journal Entries
    path('journal-entries/', views.journal_entry_list, name='journal_entry_list'),
    path('journal-entries/create/', views.journal_entry_create, name='journal_entry_create'),
    path('journal-entries/<int:pk>/', views.journal_entry_detail, name='journal_entry_detail'),
    path('journal-entries/<int:pk>/post/', views.journal_entry_post, name='journal_entry_post'),
    
    # Financial Reports
    path('reports/trial-balance/', views.trial_balance, name='trial_balance'),
    path('reports/balance-sheet/', views.balance_sheet, name='balance_sheet'),
    path('reports/income-statement/', views.income_statement, name='income_statement'),
    path('reports/ledger/', views.ledger_report, name='ledger_report'),
    
    # Fiscal Years
    path('fiscal-years/', views.fiscal_year_list, name='fiscal_year_list'),
    path('fiscal-years/create/', views.fiscal_year_create, name='fiscal_year_create'),
]
