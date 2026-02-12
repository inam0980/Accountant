from django import forms
from .models import Invoice, InvoiceItem, Payment, FeeCategory, Discount
from students.models import Student
from datetime import date, timedelta


class InvoiceForm(forms.ModelForm):
    """
    Main Invoice Form
    """
    class Meta:
        model = Invoice
        fields = ['student', 'academic_year', 'invoice_date', 'due_date', 'discount', 'notes']
        widgets = {
            'student': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'required': True
            }),
            'academic_year': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'placeholder': 'e.g., 2025-2026'
            }),
            'invoice_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'type': 'date'
            }),
            'due_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'type': 'date'
            }),
            'discount': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Additional notes or terms...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['student'].queryset = Student.objects.filter(is_active=True).order_by('name_english')
        self.fields['discount'].queryset = Discount.objects.filter(is_active=True).order_by('discount_name')
        self.fields['discount'].required = False


class InvoiceItemForm(forms.ModelForm):
    """
    Invoice Line Item Form
    """
    class Meta:
        model = InvoiceItem
        fields = ['fee_category', 'description', 'quantity', 'unit_price']
        widgets = {
            'fee_category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent'
            }),
            'description': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'placeholder': 'Optional description'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'min': '1',
                'value': '1'
            }),
            'unit_price': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': '0.00'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fee_category'].queryset = FeeCategory.objects.filter(is_active=True).order_by('category_name')


class PaymentForm(forms.ModelForm):
    """
    Payment Recording Form
    """
    class Meta:
        model = Payment
        fields = ['payment_date', 'amount', 'payment_method', 'reference_number', 
                  'cheque_number', 'bank_name', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'type': 'date'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Enter payment amount'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
            }),
            'reference_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Transaction/Reference Number'
            }),
            'cheque_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Cheque Number (if applicable)'
            }),
            'bank_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Bank Name'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Payment notes...'
            }),
        }


class InvoiceSearchForm(forms.Form):
    """
    Search and Filter Form for Invoice List
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'placeholder': 'Search by Invoice#, Student Name, or ID...'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Invoice.STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'type': 'date',
            'placeholder': 'From Date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
            'type': 'date',
            'placeholder': 'To Date'
        })
    )


class PaymentSearchForm(forms.Form):
    """
    Search and Filter Form for Payment List
    """
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Search by Payment#, Receipt#, Invoice#...'
        })
    )
    
    method = forms.ChoiceField(
        required=False,
        choices=[('', 'All Methods')] + Payment.PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[('', 'All Status')] + Payment.PAYMENT_STATUS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent'
        })
    )


class FeeCategoryForm(forms.ModelForm):
    """
    Fee Category Form (for settings)
    """
    class Meta:
        model = FeeCategory
        fields = ['category_name', 'description', 'default_amount', 'is_mandatory', 'is_active']
        widgets = {
            'category_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'placeholder': 'e.g., Tuition Fee, Transport Fee'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Description of this fee category'
            }),
            'default_amount': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Default amount in SAR'
            }),
            'is_mandatory': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-purple-600 focus:ring-purple-500 rounded'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-purple-600 focus:ring-purple-500 rounded'
            }),
        }


class DiscountForm(forms.ModelForm):
    """
    Discount Form (for settings)
    """
    class Meta:
        model = Discount
        fields = ['discount_name', 'discount_type', 'discount_value', 'description', 
                  'valid_from', 'valid_to', 'is_active']
        widgets = {
            'discount_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'placeholder': 'e.g., Early Bird Discount, Sibling Discount'
            }),
            'discount_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent'
            }),
            'discount_value': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'step': '0.01',
                'placeholder': 'Percentage or Amount'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'rows': 3,
                'placeholder': 'Discount description and terms'
            }),
            'valid_from': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'type': 'date'
            }),
            'valid_to': forms.DateInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent',
                'type': 'date'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-orange-600 focus:ring-orange-500 rounded'
            }),
        }
