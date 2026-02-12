"""
Accounting Services - Business logic for financial operations
"""
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import Account, JournalEntry, JournalEntryLine, FiscalYear, AccountType


class AccountingService:
    """Core accounting business logic service"""
    
    @staticmethod
    def create_journal_entry(school, fiscal_year, date, description, lines_data, reference="", user=None, auto_post=False):
        """
        Create a journal entry with multiple lines
        
        Args:
            school: School instance
            fiscal_year: FiscalYear instance
            date: Entry date
            description: Entry description
            lines_data: List of dicts with 'account', 'debit_amount', 'credit_amount', 'description'
            reference: Optional external reference
            user: User creating the entry
            auto_post: Whether to automatically post the entry
        
        Returns:
            JournalEntry instance
        """
        with transaction.atomic():
            entry = JournalEntry.objects.create(
                school=school,
                fiscal_year=fiscal_year,
                date=date,
                description=description,
                reference=reference,
                created_by=user,
                status='draft'
            )
            
            entry.generate_entry_number()
            entry.save()
            
            # Create lines
            for idx, line_data in enumerate(lines_data, start=1):
                JournalEntryLine.objects.create(
                    journal_entry=entry,
                    account=line_data['account'],
                    debit_amount=line_data.get('debit_amount', Decimal('0')),
                    credit_amount=line_data.get('credit_amount', Decimal('0')),
                    description=line_data.get('description', ''),
                    student=line_data.get('student'),
                    teacher=line_data.get('teacher'),
                    line_number=idx
                )
            
            # Validate and optionally post
            entry.clean()
            
            if auto_post and user:
                entry.post(user)
            
            return entry
    
    @staticmethod
    def post_invoice_to_ledger(invoice, user):
        """
        Post an invoice to the general ledger
        Creates journal entry: DR Accounts Receivable, CR Revenue, CR VAT Payable
        """
        school = invoice.school
        fiscal_year = FiscalYear.objects.filter(
            school=school,
            is_active=True,
            start_date__lte=invoice.issue_date,
            end_date__gte=invoice.issue_date
        ).first()
        
        if not fiscal_year:
            raise ValueError("No active fiscal year found for invoice date")
        
        # Get required accounts
        accounts_receivable = Account.objects.filter(
            school=school,
            code='1200',  # Standard AR account
            account_type=AccountType.ASSET
        ).first()
        
        revenue_account = Account.objects.filter(
            school=school,
            code='4000',  # Standard revenue account
            account_type=AccountType.REVENUE
        ).first()
        
        vat_payable = Account.objects.filter(
            school=school,
            code='2100',  # Standard VAT payable
            account_type=AccountType.LIABILITY
        ).first()
        
        if not all([accounts_receivable, revenue_account, vat_payable]):
            raise ValueError("Required accounts not found. Please set up chart of accounts.")
        
        # Create journal entry lines
        lines = [
            {
                'account': accounts_receivable,
                'debit_amount': invoice.total_amount,
                'credit_amount': Decimal('0'),
                'description': f"Invoice {invoice.invoice_number} - {invoice.customer_name}",
                'student': invoice.student
            },
            {
                'account': revenue_account,
                'debit_amount': Decimal('0'),
                'credit_amount': invoice.total_taxable_amount,
                'description': f"Revenue - Invoice {invoice.invoice_number}",
                'student': invoice.student
            },
            {
                'account': vat_payable,
                'debit_amount': Decimal('0'),
                'credit_amount': invoice.total_vat,
                'description': f"VAT Collected - Invoice {invoice.invoice_number}",
            }
        ]
        
        entry = AccountingService.create_journal_entry(
            school=school,
            fiscal_year=fiscal_year,
            date=invoice.issue_date,
            description=f"Invoice {invoice.invoice_number} - {invoice.customer_name}",
            lines_data=lines,
            reference=invoice.invoice_number,
            user=user,
            auto_post=True
        )
        
        # Link entry to invoice
        entry.invoice = invoice
        entry.save()
        
        return entry
    
    @staticmethod
    def post_payment_to_ledger(payment, user):
        """
        Post a payment to the general ledger
        Creates journal entry: DR Cash/Bank, CR Accounts Receivable
        """
        from billing.models import Invoice as BillingInvoice
        
        # Get invoice to determine school
        invoice = payment.invoice
        school = invoice.school
        
        fiscal_year = FiscalYear.objects.filter(
            school=school,
            is_active=True,
            start_date__lte=payment.payment_date,
            end_date__gte=payment.payment_date
        ).first()
        
        if not fiscal_year:
            raise ValueError("No active fiscal year found for payment date")
        
        # Get required accounts
        if payment.payment_method in ['cash', 'card']:
            cash_account = Account.objects.filter(
                school=school,
                code='1100',  # Cash account
                account_type=AccountType.ASSET
            ).first()
        else:
            cash_account = Account.objects.filter(
                school=school,
                code='1110',  # Bank account
                account_type=AccountType.ASSET
            ).first()
        
        accounts_receivable = Account.objects.filter(
            school=school,
            code='1200',
            account_type=AccountType.ASSET
        ).first()
        
        if not all([cash_account, accounts_receivable]):
            raise ValueError("Required accounts not found")
        
        lines = [
            {
                'account': cash_account,
                'debit_amount': payment.amount,
                'credit_amount': Decimal('0'),
                'description': f"Payment received - {payment.payment_method} - Invoice {invoice.invoice_number}",
                'student': invoice.student
            },
            {
                'account': accounts_receivable,
                'debit_amount': Decimal('0'),
                'credit_amount': payment.amount,
                'description': f"Payment applied - Invoice {invoice.invoice_number}",
                'student': invoice.student
            }
        ]
        
        entry = AccountingService.create_journal_entry(
            school=school,
            fiscal_year=fiscal_year,
            date=payment.payment_date,
            description=f"Payment - Invoice {invoice.invoice_number}",
            lines_data=lines,
            reference=payment.transaction_id or invoice.invoice_number,
            user=user,
            auto_post=True
        )
        
        entry.payment = payment
        entry.save()
        
        return entry


class FinancialReportService:
    """Generate financial reports"""
    
    @staticmethod
    def generate_trial_balance(school, fiscal_year, as_of_date=None):
        """
        Generate trial balance report
        Returns list of accounts with debit/credit balances
        """
        accounts = Account.objects.filter(
            school=school,
            is_active=True
        ).order_by('code')
        
        trial_balance = []
        total_debits = Decimal('0')
        total_credits = Decimal('0')
        
        for account in accounts:
            balance = account.get_balance(as_of_date)
            
            if balance != 0:
                if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                    debit_balance = balance if balance > 0 else Decimal('0')
                    credit_balance = abs(balance) if balance < 0 else Decimal('0')
                else:
                    debit_balance = abs(balance) if balance < 0 else Decimal('0')
                    credit_balance = balance if balance > 0 else Decimal('0')
                
                trial_balance.append({
                    'account': account,
                    'code': account.code,
                    'name': account.name,
                    'account_type': account.get_account_type_display(),
                    'debit_balance': debit_balance,
                    'credit_balance': credit_balance,
                })
                
                total_debits += debit_balance
                total_credits += credit_balance
        
        return {
            'trial_balance': trial_balance,
            'total_debits': total_debits,
            'total_credits': total_credits,
            'is_balanced': abs(total_debits - total_credits) < Decimal('0.01'),
            'fiscal_year': fiscal_year,
            'as_of_date': as_of_date or timezone.now().date()
        }
    
    @staticmethod
    def generate_balance_sheet(school, fiscal_year, as_of_date=None):
        """
        Generate balance sheet: Assets = Liabilities + Equity
        """
        accounts = Account.objects.filter(
            school=school,
            is_active=True
        ).order_by('code')
        
        assets = []
        liabilities = []
        equity = []
        
        total_assets = Decimal('0')
        total_liabilities = Decimal('0')
        total_equity = Decimal('0')
        
        for account in accounts:
            balance = account.get_balance(as_of_date)
            
            if balance != 0:
                account_data = {
                    'account': account,
                    'code': account.code,
                    'name': account.name,
                    'balance': abs(balance)
                }
                
                if account.account_type == AccountType.ASSET:
                    assets.append(account_data)
                    total_assets += abs(balance)
                elif account.account_type == AccountType.LIABILITY:
                    liabilities.append(account_data)
                    total_liabilities += abs(balance)
                elif account.account_type == AccountType.EQUITY:
                    equity.append(account_data)
                    total_equity += abs(balance)
        
        return {
            'assets': assets,
            'liabilities': liabilities,
            'equity': equity,
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_equity': total_equity,
            'is_balanced': abs(total_assets - (total_liabilities + total_equity)) < Decimal('0.01'),
            'fiscal_year': fiscal_year,
            'as_of_date': as_of_date or timezone.now().date()
        }
    
    @staticmethod
    def generate_income_statement(school, fiscal_year, start_date=None, end_date=None):
        """
        Generate profit & loss statement: Revenue - Expenses = Net Income
        """
        if not start_date:
            start_date = fiscal_year.start_date
        if not end_date:
            end_date = fiscal_year.end_date
        
        # Get all journal lines within period
        from django.db.models import Sum, Q
        
        accounts = Account.objects.filter(
            school=school,
            is_active=True,
            account_type__in=[AccountType.REVENUE, AccountType.EXPENSE]
        ).order_by('code')
        
        revenue = []
        expenses = []
        
        total_revenue = Decimal('0')
        total_expenses = Decimal('0')
        
        for account in accounts:
            # Get transactions within period
            journal_lines = account.journal_lines.filter(
                journal_entry__status='posted',
                journal_entry__date__gte=start_date,
                journal_entry__date__lte=end_date
            )
            
            debits = journal_lines.aggregate(total=Sum('debit_amount'))['total'] or Decimal('0')
            credits = journal_lines.aggregate(total=Sum('credit_amount'))['total'] or Decimal('0')
            
            if account.account_type == AccountType.REVENUE:
                balance = credits - debits  # Revenue is credit balance
            else:
                balance = debits - credits  # Expense is debit balance
            
            if balance != 0:
                account_data = {
                    'account': account,
                    'code': account.code,
                    'name': account.name,
                    'balance': abs(balance)
                }
                
                if account.account_type == AccountType.REVENUE:
                    revenue.append(account_data)
                    total_revenue += abs(balance)
                else:
                    expenses.append(account_data)
                    total_expenses += abs(balance)
        
        net_income = total_revenue - total_expenses
        
        return {
            'revenue': revenue,
            'expenses': expenses,
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'net_income': net_income,
            'fiscal_year': fiscal_year,
            'start_date': start_date,
            'end_date': end_date
        }
    
    @staticmethod
    def generate_ledger_report(account, start_date=None, end_date=None):
        """
        Generate account ledger showing all transactions
        """
        journal_lines = account.journal_lines.filter(
            journal_entry__status='posted'
        ).select_related('journal_entry').order_by('journal_entry__date', 'journal_entry__entry_number')
        
        if start_date:
            journal_lines = journal_lines.filter(journal_entry__date__gte=start_date)
        if end_date:
            journal_lines = journal_lines.filter(journal_entry__date__lte=end_date)
        
        running_balance = account.opening_balance if account.opening_balance_type == 'debit' else -account.opening_balance
        
        ledger_entries = []
        
        for line in journal_lines:
            if account.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
                running_balance += line.debit_amount - line.credit_amount
            else:
                running_balance += line.credit_amount - line.debit_amount
            
            ledger_entries.append({
                'date': line.journal_entry.date,
                'entry_number': line.journal_entry.entry_number,
                'description': line.description or line.journal_entry.description,
                'reference': line.journal_entry.reference,
                'debit': line.debit_amount,
                'credit': line.credit_amount,
                'balance': running_balance
            })
        
        return {
            'account': account,
            'opening_balance': account.opening_balance,
            'opening_balance_type': account.opening_balance_type,
            'ledger_entries': ledger_entries,
            'closing_balance': running_balance,
            'start_date': start_date,
            'end_date': end_date
        }


class ChartOfAccountsSetup:
    """Setup default chart of accounts for a school"""
    
    @staticmethod
    def create_default_accounts(school, user=None):
        """Create standard chart of accounts"""
        accounts_data = [
            # Assets (1000-1999)
            {'code': '1000', 'name': 'Assets', 'name_arabic': 'الأصول', 'type': AccountType.ASSET, 'parent': None, 'system': True},
            {'code': '1100', 'name': 'Cash', 'name_arabic': 'النقدية', 'type': AccountType.ASSET, 'parent': '1000', 'system': True},
            {'code': '1110', 'name': 'Bank Account', 'name_arabic': 'الحساب البنكي', 'type': AccountType.ASSET, 'parent': '1000', 'system': True},
            {'code': '1200', 'name': 'Accounts Receivable', 'name_arabic': 'الذمم المدينة', 'type': AccountType.ASSET, 'parent': '1000', 'system': True},
            {'code': '1300', 'name': 'Inventory', 'name_arabic': 'المخزون', 'type': AccountType.ASSET, 'parent': '1000', 'system': True},
            {'code': '1500', 'name': 'Fixed Assets', 'name_arabic': 'الأصول الثابتة', 'type': AccountType.ASSET, 'parent': '1000', 'system': True},
            
            # Liabilities (2000-2999)
            {'code': '2000', 'name': 'Liabilities', 'name_arabic': 'الخصوم', 'type': AccountType.LIABILITY, 'parent': None, 'system': True},
            {'code': '2100', 'name': 'VAT Payable', 'name_arabic': 'ضريبة القيمة المضافة المستحقة', 'type': AccountType.LIABILITY, 'parent': '2000', 'system': True},
            {'code': '2200', 'name': 'Accounts Payable', 'name_arabic': 'الذمم الدائنة', 'type': AccountType.LIABILITY, 'parent': '2000', 'system': True},
            {'code': '2300', 'name': 'Salaries Payable', 'name_arabic': 'الرواتب المستحقة', 'type': AccountType.LIABILITY, 'parent': '2000', 'system': True},
            {'code': '2400', 'name': 'Loans Payable', 'name_arabic': 'القروض المستحقة', 'type': AccountType.LIABILITY, 'parent': '2000', 'system': True},
            
            # Equity (3000-3999)
            {'code': '3000', 'name': 'Equity', 'name_arabic': 'حقوق الملكية', 'type': AccountType.EQUITY, 'parent': None, 'system': True},
            {'code': '3100', 'name': 'Capital', 'name_arabic': 'رأس المال', 'type': AccountType.EQUITY, 'parent': '3000', 'system': True},
            {'code': '3200', 'name': 'Retained Earnings', 'name_arabic': 'الأرباح المحتجزة', 'type': AccountType.EQUITY, 'parent': '3000', 'system': True},
            
            # Revenue (4000-4999)
            {'code': '4000', 'name': 'Revenue', 'name_arabic': 'الإيرادات', 'type': AccountType.REVENUE, 'parent': None, 'system': True},
            {'code': '4100', 'name': 'Tuition Fees', 'name_arabic': 'الرسوم الدراسية', 'type': AccountType.REVENUE, 'parent': '4000', 'system': True},
            {'code': '4200', 'name': 'Transport Fees', 'name_arabic': 'رسوم النقل', 'type': AccountType.REVENUE, 'parent': '4000', 'system': True},
            {'code': '4300', 'name': 'Hostel Fees', 'name_arabic': 'رسوم السكن', 'type': AccountType.REVENUE, 'parent': '4000', 'system': True},
            {'code': '4400', 'name': 'Other Income', 'name_arabic': 'الدخل الآخر', 'type': AccountType.REVENUE, 'parent': '4000', 'system': True},
            
            # Expenses (5000-5999)
            {'code': '5000', 'name': 'Expenses', 'name_arabic': 'المصروفات', 'type': AccountType.EXPENSE, 'parent': None, 'system': True},
            {'code': '5100', 'name': 'Salaries Expense', 'name_arabic': 'مصروف الرواتب', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
            {'code': '5200', 'name': 'Rent Expense', 'name_arabic': 'مصروف الإيجار', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
            {'code': '5300', 'name': 'Utilities Expense', 'name_arabic': 'مصروف المرافق', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
            {'code': '5400', 'name': 'Supplies Expense', 'name_arabic': 'مصروف اللوازم', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
            {'code': '5500', 'name': 'Maintenance Expense', 'name_arabic': 'مصروف الصيانة', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
            {'code': '5600', 'name': 'Marketing Expense', 'name_arabic': 'مصروف التسويق', 'type': AccountType.EXPENSE, 'parent': '5000', 'system': True},
        ]
        
        created_accounts = {}
        
        with transaction.atomic():
            for acc_data in accounts_data:
                parent = None
                if acc_data['parent']:
                    parent = created_accounts.get(acc_data['parent'])
                
                account = Account.objects.create(
                    school=school,
                    code=acc_data['code'],
                    name=acc_data['name'],
                    name_arabic=acc_data['name_arabic'],
                    account_type=acc_data['type'],
                    parent=parent,
                    is_system=acc_data['system'],
                    created_by=user
                )
                
                created_accounts[acc_data['code']] = account
        
        return created_accounts
