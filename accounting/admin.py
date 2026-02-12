from django.contrib import admin
from .models import Account, JournalEntry, JournalEntryLine, FiscalYear, AccountingPeriod, BudgetLine


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'account_type', 'parent', 'current_balance', 'is_active', 'is_system']
    list_filter = ['account_type', 'is_active', 'is_system', 'school']
    search_fields = ['code', 'name', 'name_arabic']
    ordering = ['code']
    readonly_fields = ['current_balance', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('school', 'code', 'name', 'name_arabic', 'account_type', 'parent')
        }),
        ('Account Behavior', {
            'fields': ('is_active', 'is_system', 'allow_manual_entries')
        }),
        ('Financial Data', {
            'fields': ('opening_balance', 'opening_balance_type', 'current_balance')
        }),
        ('Metadata', {
            'fields': ('description', 'created_by', 'created_at', 'updated_at')
        }),
    )


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2
    fields = ['line_number', 'account', 'description', 'debit_amount', 'credit_amount']
    readonly_fields = []


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ['entry_number', 'date', 'school', 'fiscal_year', 'status', 'total_debit', 'total_credit', 'created_by']
    list_filter = ['status', 'school', 'fiscal_year', 'date']
    search_fields = ['entry_number', 'description', 'reference']
    ordering = ['-date', '-entry_number']
    readonly_fields = ['entry_number', 'total_debit', 'total_credit', 'posted_by', 'posted_at', 'created_at', 'updated_at']
    inlines = [JournalEntryLineInline]
    
    fieldsets = (
        ('Entry Information', {
            'fields': ('school', 'fiscal_year', 'entry_number', 'date', 'status')
        }),
        ('Details', {
            'fields': ('reference', 'description')
        }),
        ('Linked Transactions', {
            'fields': ('invoice', 'billing_invoice', 'payment'),
            'classes': ('collapse',)
        }),
        ('Totals', {
            'fields': ('total_debit', 'total_credit')
        }),
        ('Workflow', {
            'fields': ('created_by', 'posted_by', 'posted_at', 'created_at', 'updated_at')
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Make fields readonly if entry is posted"""
        readonly = list(self.readonly_fields)
        if obj and obj.status == 'posted':
            readonly.extend(['school', 'fiscal_year', 'date', 'reference', 'description'])
        return readonly


@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ['name', 'school', 'start_date', 'end_date', 'is_active', 'is_closed']
    list_filter = ['is_active', 'is_closed', 'school']
    search_fields = ['name']
    ordering = ['-start_date']
    readonly_fields = ['closed_by', 'closed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Fiscal Year Information', {
            'fields': ('school', 'name', 'start_date', 'end_date')
        }),
        ('Status', {
            'fields': ('is_active', 'is_closed', 'closed_by', 'closed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(AccountingPeriod)
class AccountingPeriodAdmin(admin.ModelAdmin):
    list_display = ['name', 'fiscal_year', 'period_number', 'start_date', 'end_date', 'is_closed']
    list_filter = ['is_closed', 'fiscal_year']
    ordering = ['fiscal_year', 'period_number']


@admin.register(BudgetLine)
class BudgetLineAdmin(admin.ModelAdmin):
    list_display = ['account', 'fiscal_year', 'budgeted_amount', 'actual_amount', 'variance']
    list_filter = ['fiscal_year', 'school']
    search_fields = ['account__code', 'account__name']
    readonly_fields = ['actual_amount', 'variance', 'created_at', 'updated_at']
