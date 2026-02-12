from django.contrib import admin
from .models import FeeCategory, Discount, Invoice, InvoiceItem, Payment

# Register your models here.

@admin.register(FeeCategory)
class FeeCategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'default_amount', 'is_mandatory', 'is_active', 'created_at']
    list_filter = ['is_mandatory', 'is_active', 'created_at']
    search_fields = ['category_name', 'description']
    list_editable = ['is_active']
    ordering = ['category_name']


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ['discount_name', 'discount_type', 'discount_value', 'valid_from', 'valid_to', 'is_active']
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_to']
    search_fields = ['discount_name', 'description']
    list_editable = ['is_active']
    date_hierarchy = 'valid_from'
    ordering = ['-created_at']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1
    fields = ['fee_category', 'description', 'quantity', 'unit_price', 'total_amount']
    readonly_fields = ['total_amount']


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0
    fields = ['payment_number', 'payment_date', 'amount', 'payment_method', 'reference_number', 'status']
    readonly_fields = ['payment_number']
    can_delete = False


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'student', 'invoice_date', 'due_date', 'total_amount', 'paid_amount', 'balance_amount', 'status']
    list_filter = ['status', 'invoice_date', 'due_date', 'academic_year']
    search_fields = ['invoice_number', 'student__name_english', 'student__name_arabic', 'student__student_id']
    readonly_fields = ['invoice_number', 'subtotal', 'discount_amount', 'vat_amount', 'total_amount', 'paid_amount', 'balance_amount', 'created_at', 'updated_at']
    date_hierarchy = 'invoice_date'
    ordering = ['-invoice_date', '-invoice_number']
    inlines = [InvoiceItemInline, PaymentInline]
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('invoice_number', 'student', 'academic_year', 'invoice_date', 'due_date', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'discount', 'discount_amount', 'vat_amount', 'total_amount', 'paid_amount', 'balance_amount')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(InvoiceItem)
class InvoiceItemAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'fee_category', 'quantity', 'unit_price', 'total_amount']
    list_filter = ['fee_category', 'invoice__invoice_date']
    search_fields = ['invoice__invoice_number', 'fee_category__category_name']
    readonly_fields = ['total_amount']
    ordering = ['-invoice__invoice_date']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_number', 'invoice', 'payment_date', 'amount', 'payment_method', 'status', 'received_by']
    list_filter = ['status', 'payment_method', 'payment_date']
    search_fields = ['payment_number', 'invoice__invoice_number', 'receipt_number', 'reference_number']
    readonly_fields = ['payment_number', 'receipt_number', 'payment_time', 'created_at', 'updated_at']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date', '-payment_time']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_number', 'invoice', 'payment_date', 'payment_time', 'amount', 'status')
        }),
        ('Payment Method Details', {
            'fields': ('payment_method', 'reference_number', 'cheque_number', 'bank_name')
        }),
        ('Receipt Information', {
            'fields': ('receipt_number', 'notes', 'received_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.received_by = request.user
        super().save_model(request, obj, form, change)
