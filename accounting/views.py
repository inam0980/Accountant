from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Q
from django.utils import timezone
from decimal import Decimal

from .models import Account, JournalEntry, JournalEntryLine, FiscalYear, BudgetLine, AccountType
from .forms import (
    AccountForm, JournalEntryForm, JournalEntryLineForm, FiscalYearForm,
    BudgetLineForm, TrialBalanceFilterForm, BalanceSheetFilterForm,
    IncomeStatementFilterForm, LedgerReportFilterForm, get_journal_entry_line_formset
)
from .services import AccountingService, FinancialReportService, ChartOfAccountsSetup
from accounts.decorators import module_required, action_required


@module_required('accounting')
def accounting_dashboard(request):
    """Accounting dashboard with key metrics"""
    school = request.school
    
    # Get active fiscal year
    fiscal_year = FiscalYear.objects.filter(
        school=school,
        is_active=True
    ).first()
    
    if not fiscal_year:
        messages.warning(request, "No active fiscal year found. Please create one.")
        return redirect('accounting:fiscal_year_list')
    
    # Key metrics
    total_assets = Account.objects.filter(
        school=school,
        account_type=AccountType.ASSET,
        is_active=True
    ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    
    total_liabilities = Account.objects.filter(
        school=school,
        account_type=AccountType.LIABILITY,
        is_active=True
    ).aggregate(total=Sum('current_balance'))['total'] or Decimal('0')
    
    # Recent journal entries
    recent_entries = JournalEntry.objects.filter(
        school=school,
        fiscal_year=fiscal_year
    ).order_by('-date', '-created_at')[:10]
    
    # Accounts receivable
    ar_account = Account.objects.filter(
        school=school,
        code='1200'
    ).first()
    
    accounts_receivable = ar_account.current_balance if ar_account else Decimal('0')
    
    context = {
        'fiscal_year': fiscal_year,
        'total_assets': total_assets,
        'total_liabilities': total_liabilities,
        'accounts_receivable': accounts_receivable,
        'net_worth': total_assets - total_liabilities,
        'recent_entries': recent_entries,
    }
    
    return render(request, 'accounting/dashboard.html', context)


@action_required('accounting', 'view_accounts')
def chart_of_accounts(request):
    """List all accounts in chart of accounts"""
    school = request.school
    accounts = Account.objects.filter(
        school=school
    ).select_related('parent').order_by('code')
    
    # Group by account type
    accounts_by_type = {}
    for account in accounts:
        acc_type = account.get_account_type_display()
        if acc_type not in accounts_by_type:
            accounts_by_type[acc_type] = []
        accounts_by_type[acc_type].append(account)
    
    context = {
        'accounts_by_type': accounts_by_type,
        'total_accounts': accounts.count()
    }
    
    return render(request, 'accounting/chart_of_accounts.html', context)


@action_required('accounting', 'create_account')
def account_create(request):
    """Create a new account"""
    school = request.school
    
    if request.method == 'POST':
        form = AccountForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.school = school
            account.created_by = request.user
            account.save()
            messages.success(request, f"Account {account.code} - {account.name} created successfully")
            return redirect('accounting:chart_of_accounts')
    else:
        form = AccountForm()
    
    # Filter parent accounts by school
    form.fields['parent'].queryset = Account.objects.filter(school=school)
    
    return render(request, 'accounting/account_form.html', {'form': form, 'action': 'Create'})


@action_required('accounting', 'view_journal')
def journal_entry_list(request):
    """List all journal entries"""
    school = request.school
    fiscal_year_id = request.GET.get('fiscal_year')
    
    entries = JournalEntry.objects.filter(school=school)
    
    if fiscal_year_id:
        entries = entries.filter(fiscal_year_id=fiscal_year_id)
    
    entries = entries.select_related('fiscal_year', 'created_by').order_by('-date', '-entry_number')
    
    fiscal_years = FiscalYear.objects.filter(school=school)
    
    context = {
        'entries': entries,
        'fiscal_years': fiscal_years,
        'selected_fiscal_year': fiscal_year_id
    }
    
    return render(request, 'accounting/journal_entry_list.html', context)


@action_required('accounting', 'create_journal')
def journal_entry_create(request):
    """Create a new journal entry"""
    school = request.school
    JournalEntryLineFormSet = get_journal_entry_line_formset()
    
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        formset = JournalEntryLineFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                entry = form.save(commit=False)
                entry.school = school
                entry.created_by = request.user
                entry.generate_entry_number()
                entry.save()
                
                formset.instance = entry
                formset.save()
                
                # Validate entry balances
                entry.clean()
                
                messages.success(request, f"Journal Entry {entry.entry_number} created successfully")
                return redirect('accounting:journal_entry_detail', pk=entry.pk)
            
            except Exception as e:
                messages.error(request, f"Error creating journal entry: {str(e)}")
    else:
        form = JournalEntryForm()
        formset = JournalEntryLineFormSet()
    
    # Filter fiscal years and accounts by school
    form.fields['fiscal_year'].queryset = FiscalYear.objects.filter(school=school, is_active=True)
    
    for form_line in formset:
        form_line.fields['account'].queryset = Account.objects.filter(
            school=school,
            is_active=True,
            allow_manual_entries=True
        ).order_by('code')
    
    context = {
        'form': form,
        'formset': formset,
        'action': 'Create'
    }
    
    return render(request, 'accounting/journal_entry_form.html', context)


@action_required('accounting', 'view_journal')
def journal_entry_detail(request, pk):
    """View journal entry details"""
    school = request.school
    entry = get_object_or_404(JournalEntry, pk=pk, school=school)
    lines = entry.lines.all().select_related('account')
    
    context = {
        'entry': entry,
        'lines': lines
    }
    
    return render(request, 'accounting/journal_entry_detail.html', context)


@action_required('accounting', 'post_journal')
def journal_entry_post(request, pk):
    """Post a draft journal entry"""
    school = request.school
    entry = get_object_or_404(JournalEntry, pk=pk, school=school)
    
    if request.method == 'POST':
        try:
            entry.post(request.user)
            messages.success(request, f"Journal Entry {entry.entry_number} posted successfully")
        except Exception as e:
            messages.error(request, f"Error posting entry: {str(e)}")
    
    return redirect('accounting:journal_entry_detail', pk=pk)


@action_required('accounting', 'view_reports')
def trial_balance(request):
    """Generate trial balance report"""
    school = request.school
    
    if request.method == 'GET' and 'fiscal_year' in request.GET:
        form = TrialBalanceFilterForm(school, request.GET)
        if form.is_valid():
            fiscal_year = form.cleaned_data['fiscal_year']
            as_of_date = form.cleaned_data.get('as_of_date')
            
            report_data = FinancialReportService.generate_trial_balance(
                school, fiscal_year, as_of_date
            )
            
            context = {
                'form': form,
                'report_data': report_data
            }
            
            return render(request, 'accounting/trial_balance.html', context)
    else:
        form = TrialBalanceFilterForm(school)
    
    return render(request, 'accounting/trial_balance.html', {'form': form})


@action_required('accounting', 'view_reports')
def balance_sheet(request):
    """Generate balance sheet report"""
    school = request.school
    
    if request.method == 'GET' and 'fiscal_year' in request.GET:
        form = BalanceSheetFilterForm(school, request.GET)
        if form.is_valid():
            fiscal_year = form.cleaned_data['fiscal_year']
            as_of_date = form.cleaned_data.get('as_of_date')
            
            report_data = FinancialReportService.generate_balance_sheet(
                school, fiscal_year, as_of_date
            )
            
            context = {
                'form': form,
                'report_data': report_data
            }
            
            return render(request, 'accounting/balance_sheet.html', context)
    else:
        form = BalanceSheetFilterForm(school)
    
    return render(request, 'accounting/balance_sheet.html', {'form': form})


@action_required('accounting', 'view_reports')
def income_statement(request):
    """Generate income statement (P&L) report"""
    school = request.school
    
    if request.method == 'GET' and 'fiscal_year' in request.GET:
        form = IncomeStatementFilterForm(school, request.GET)
        if form.is_valid():
            fiscal_year = form.cleaned_data['fiscal_year']
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            
            report_data = FinancialReportService.generate_income_statement(
                school, fiscal_year, start_date, end_date
            )
            
            context = {
                'form': form,
                'report_data': report_data
            }
            
            return render(request, 'accounting/income_statement.html', context)
    else:
        form = IncomeStatementFilterForm(school)
    
    return render(request, 'accounting/income_statement.html', {'form': form})


@action_required('accounting', 'view_reports')
def ledger_report(request):
    """Generate account ledger report"""
    school = request.school
    
    if request.method == 'GET' and 'account' in request.GET:
        form = LedgerReportFilterForm(school, request.GET)
        if form.is_valid():
            account = form.cleaned_data['account']
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            
            report_data = FinancialReportService.generate_ledger_report(
                account, start_date, end_date
            )
            
            context = {
                'form': form,
                'report_data': report_data
            }
            
            return render(request, 'accounting/ledger_report.html', context)
    else:
        form = LedgerReportFilterForm(school)
    
    return render(request, 'accounting/ledger_report.html', {'form': form})


@action_required('accounting', 'manage_fiscal_year')
def fiscal_year_list(request):
    """List all fiscal years"""
    school = request.school
    fiscal_years = FiscalYear.objects.filter(school=school).order_by('-start_date')
    
    return render(request, 'accounting/fiscal_year_list.html', {'fiscal_years': fiscal_years})


@action_required('accounting', 'manage_fiscal_year')
def fiscal_year_create(request):
    """Create a new fiscal year"""
    school = request.school
    
    if request.method == 'POST':
        form = FiscalYearForm(request.POST)
        if form.is_valid():
            fiscal_year = form.save(commit=False)
            fiscal_year.school = school
            fiscal_year.save()
            messages.success(request, f"Fiscal Year {fiscal_year.name} created successfully")
            return redirect('accounting:fiscal_year_list')
    else:
        form = FiscalYearForm()
    
    return render(request, 'accounting/fiscal_year_form.html', {'form': form, 'action': 'Create'})


@action_required('accounting', 'setup_accounts')
def setup_chart_of_accounts(request):
    """Setup default chart of accounts for a school"""
    school = request.school
    
    # Check if accounts already exist
    existing_accounts = Account.objects.filter(school=school).count()
    
    if existing_accounts > 0:
        messages.warning(request, "Chart of accounts already exists for this school")
        return redirect('accounting:chart_of_accounts')
    
    if request.method == 'POST':
        try:
            ChartOfAccountsSetup.create_default_accounts(school, request.user)
            messages.success(request, "Default chart of accounts created successfully")
            return redirect('accounting:chart_of_accounts')
        except Exception as e:
            messages.error(request, f"Error creating chart of accounts: {str(e)}")
    
    return render(request, 'accounting/setup_chart_of_accounts.html')
