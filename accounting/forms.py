from django import forms
from django.core.exceptions import ValidationError
from .models import Account, JournalEntry, JournalEntryLine, FiscalYear, BudgetLine, AccountType
from decimal import Decimal


class FiscalYearForm(forms.ModelForm):
    class Meta:
        model = FiscalYear
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., FY 2024-2025'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = [
            'code', 'name', 'name_arabic', 'account_type', 'parent',
            'is_active', 'allow_manual_entries', 'opening_balance',
            'opening_balance_type', 'description'
        ]
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '1000'}),
            'name': forms.TextInput(attrs={'class': 'form-input'}),
            'name_arabic': forms.TextInput(attrs={'class': 'form-input', 'dir': 'rtl'}),
            'account_type': forms.Select(attrs={'class': 'form-select'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'opening_balance': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'opening_balance_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = ['fiscal_year', 'date', 'reference', 'description']
        widgets = {
            'fiscal_year': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
            'reference': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Invoice #, Receipt #, etc.'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class JournalEntryLineForm(forms.ModelForm):
    class Meta:
        model = JournalEntryLine
        fields = ['account', 'description', 'debit_amount', 'credit_amount']
        widgets = {
            'account': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-input'}),
            'debit_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'credit_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
        }


def get_journal_entry_line_formset():
    """Factory function to create formset after models are loaded"""
    from django.forms import inlineformset_factory
    
    return inlineformset_factory(
        JournalEntry,
        JournalEntryLine,
        form=JournalEntryLineForm,
        extra=4,  # Show 4 blank lines
        can_delete=True,
        min_num=2,  # Minimum 2 lines (debit and credit)
        validate_min=True
    )


class BudgetLineForm(forms.ModelForm):
    class Meta:
        model = BudgetLine
        fields = ['fiscal_year', 'account', 'budgeted_amount', 'notes']
        widgets = {
            'fiscal_year': forms.Select(attrs={'class': 'form-select'}),
            'account': forms.Select(attrs={'class': 'form-select'}),
            'budgeted_amount': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01'}),
            'notes': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
        }


class TrialBalanceFilterForm(forms.Form):
    """Filter form for trial balance report"""
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    as_of_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(
            school=school
        ).order_by('-start_date')


class BalanceSheetFilterForm(forms.Form):
    """Filter form for balance sheet report"""
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    as_of_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(
            school=school
        ).order_by('-start_date')


class IncomeStatementFilterForm(forms.Form):
    """Filter form for income statement report"""
    fiscal_year = forms.ModelChoiceField(
        queryset=FiscalYear.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fiscal_year'].queryset = FiscalYear.objects.filter(
            school=school
        ).order_by('-start_date')


class LedgerReportFilterForm(forms.Form):
    """Filter form for account ledger report"""
    account = forms.ModelChoiceField(
        queryset=Account.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'})
    )
    
    def __init__(self, school, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account'].queryset = Account.objects.filter(
            school=school,
            is_active=True
        ).order_by('code')
