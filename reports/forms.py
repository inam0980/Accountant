from django import forms
from django.utils import timezone
from students.models import Student
from .models import ReportTemplate, SavedReport


class DateRangeForm(forms.Form):
    """Form for selecting date range"""
    date_from = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        required=False,
        label='From Date'
    )
    date_to = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        required=False,
        label='To Date'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set default dates to current month
        if not self.is_bound:
            today = timezone.now().date()
            first_day = today.replace(day=1)
            self.initial['date_from'] = first_day
            self.initial['date_to'] = today


class StudentReportFilterForm(forms.Form):
    """Filter form for student reports"""
    status = forms.ChoiceField(
        choices=[('', 'All Status'), ('active', 'Active'), ('inactive', 'Inactive')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        label='Student Status'
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
            'placeholder': 'Search by name or admission number...'
        }),
        label='Search'
    )


class FinancialReportFilterForm(DateRangeForm):
    """Filter form for financial reports"""
    payment_status = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('partially_paid', 'Partially Paid'),
            ('overdue', 'Overdue'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        label='Payment Status'
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('', 'All Methods'),
            ('cash', 'Cash'),
            ('card', 'Card'),
            ('bank_transfer', 'Bank Transfer'),
            ('cheque', 'Cheque'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent'
        }),
        label='Payment Method'
    )


class FeeCollectionReportForm(DateRangeForm):
    """Form for fee collection report"""
    min_outstanding = forms.DecimalField(
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
            'placeholder': '0.00'
        }),
        label='Minimum Outstanding Amount'
    )


class ExportReportForm(forms.Form):
    """Form for exporting reports"""
    EXPORT_FORMATS = [
        ('pdf', 'PDF Document'),
        ('excel', 'Excel Spreadsheet'),
        ('csv', 'CSV File'),
    ]
    
    format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.RadioSelect(attrs={
            'class': 'mr-2'
        }),
        label='Export Format',
        initial='pdf'
    )
    include_charts = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label='Include Charts and Graphs'
    )
    include_summary = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label='Include Summary Statistics'
    )


class SaveReportForm(forms.ModelForm):
    """Form for saving a report"""
    class Meta:
        model = SavedReport
        fields = ['title', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'Enter report title...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Add notes about this report...'
            }),
        }
