from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from accounts.decorators import module_required, action_required
from students.models import Student
from billing.models import Invoice, Payment
from .models import ReportTemplate, SavedReport, ScheduledReport


@login_required
@module_required('reports')
def reports_dashboard(request):
    """Main reports dashboard"""
    context = {
        'total_templates': ReportTemplate.objects.filter(is_active=True).count(),
        'saved_reports': SavedReport.objects.count(),
        'recent_reports': SavedReport.objects.all()[:5],
        'scheduled_reports': ScheduledReport.objects.filter(is_active=True).count(),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@module_required('reports')
def student_report(request):
    """Generate student-related reports"""
    students = Student.objects.all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    
    if status_filter:
        students = students.filter(is_active=(status_filter == 'active'))
    
    # Statistics
    total_students = students.count()
    active_students = students.filter(is_active=True).count()
    inactive_students = students.filter(is_active=False).count()
    
    context = {
        'students': students,
        'total_students': total_students,
        'active_students': active_students,
        'inactive_students': inactive_students,
        'status_filter': status_filter,
    }
    return render(request, 'reports/student_report.html', context)


@login_required
@module_required('reports')
def financial_report(request):
    """Generate financial reports"""
    # Date range filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default to current month
    if not date_from:
        date_from = timezone.now().replace(day=1).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Query invoices
    invoices = Invoice.objects.filter(
        invoice_date__range=[date_from, date_to]
    )
    
    payments = Payment.objects.filter(
        payment_date__range=[date_from, date_to]
    )
    
    # Calculate totals
    total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_paid = payments.aggregate(total=Sum('amount'))['total'] or Decimal('0')
    total_vat = invoices.aggregate(total=Sum('vat_amount'))['total'] or Decimal('0')
    
    # Outstanding
    outstanding_invoices = Invoice.objects.filter(status__in=['pending', 'partially_paid'])
    total_outstanding = outstanding_invoices.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0')
    
    # Monthly breakdown
    from django.db.models.functions import TruncMonth
    monthly_revenue = payments.annotate(
        month=TruncMonth('payment_date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Payment method breakdown
    payment_methods = payments.values('payment_method').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'total_invoiced': total_invoiced,
        'total_paid': total_paid,
        'total_vat': total_vat,
        'total_outstanding': total_outstanding,
        'invoices': invoices,
        'payments': payments,
        'monthly_revenue': list(monthly_revenue),
        'payment_methods': payment_methods,
        'outstanding_count': outstanding_invoices.count(),
    }
    return render(request, 'reports/financial_report.html', context)


@login_required
@module_required('reports')
def fee_collection_report(request):
    """Fee collection summary report"""
    # Date range
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Default to current month
    if not date_from:
        date_from = timezone.now().replace(day=1).date()
    else:
        date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
    
    if not date_to:
        date_to = timezone.now().date()
    else:
        date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
    
    # Base query
    students = Student.objects.filter(is_active=True)
    
    # Collection data
    collection_data = []
    total_expected = Decimal('0')
    total_collected = Decimal('0')
    total_outstanding = Decimal('0')
    
    for student in students:
        # Get student's invoices
        student_invoices = Invoice.objects.filter(
            student=student,
            invoice_date__range=[date_from, date_to]
        )
        
        expected = student_invoices.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        paid = Payment.objects.filter(
            invoice__in=student_invoices,
            payment_date__range=[date_from, date_to]
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        
        outstanding = expected - paid
        
        collection_data.append({
            'student': student,
            'expected': expected,
            'collected': paid,
            'outstanding': outstanding,
            'collection_rate': (paid / expected * 100) if expected > 0 else 0
        })
        
        total_expected += expected
        total_collected += paid
        total_outstanding += outstanding
    
    overall_rate = (total_collected / total_expected * 100) if total_expected > 0 else 0
    
    context = {
        'date_from': date_from,
        'date_to': date_to,
        'collection_data': collection_data,
        'total_expected': total_expected,
        'total_collected': total_collected,
        'total_outstanding': total_outstanding,
        'overall_rate': overall_rate,
    }
    return render(request, 'reports/fee_collection_report.html', context)


@login_required
@module_required('reports')
def outstanding_fees_report(request):
    """Report of all outstanding fees"""
    
    # Get all students with outstanding balances
    outstanding_data = []
    
    students = Student.objects.filter(is_active=True)
    
    for student in students:
        pending_invoices = Invoice.objects.filter(
            student=student,
            status__in=['pending', 'partially_paid']
        )
        
        if pending_invoices.exists():
            total_outstanding = pending_invoices.aggregate(
                total=Sum('total_amount')
            )['total'] or Decimal('0')
            
            paid_amount = Payment.objects.filter(
                invoice__in=pending_invoices
            ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
            
            balance = total_outstanding - paid_amount
            
            if balance > 0:
                # Find oldest unpaid invoice
                oldest_invoice = pending_invoices.order_by('invoice_date').first()
                days_overdue = (timezone.now().date() - oldest_invoice.invoice_date).days
                
                outstanding_data.append({
                    'student': student,
                    'total_outstanding': balance,
                    'invoice_count': pending_invoices.count(),
                    'oldest_invoice_date': oldest_invoice.invoice_date,
                    'days_overdue': days_overdue,
                })
    
    # Sort by outstanding amount
    outstanding_data.sort(key=lambda x: x['total_outstanding'], reverse=True)
    
    total_outstanding = sum(item['total_outstanding'] for item in outstanding_data)
    
    context = {
        'outstanding_data': outstanding_data,
        'total_outstanding': total_outstanding,
        'total_students': len(outstanding_data),
    }
    return render(request, 'reports/outstanding_fees_report.html', context)


@login_required
@module_required('reports')
@action_required('reports', 'export')
def export_report(request, report_type):
    """Export reports to PDF or Excel"""
    export_format = request.GET.get('format', 'pdf')
    
    if export_format == 'pdf':
        return export_to_pdf(request, report_type)
    elif export_format == 'excel':
        return export_to_excel(request, report_type)
    else:
        return HttpResponse("Invalid format", status=400)


def export_to_pdf(request, report_type):
    """Export report to PDF format"""
    # This is a placeholder - will be implemented with reportlab
    from django.template.loader import render_to_string
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.pdf"'
    
    # TODO: Implement PDF generation with reportlab
    response.write(b"PDF generation will be implemented")
    
    return response


def export_to_excel(request, report_type):
    """Export report to Excel format"""
    # This is a placeholder - will be implemented with openpyxl
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.xlsx"'
    
    # TODO: Implement Excel generation with openpyxl
    response.write(b"Excel generation will be implemented")
    
    return response


@login_required
@module_required('reports')
def save_report(request):
    """Save a generated report for future reference"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        title = request.POST.get('title')
        data = request.POST.get('data')
        
        saved_report = SavedReport.objects.create(
            title=title,
            report_type=report_type,
            generated_by=request.user,
            data=json.loads(data) if data else {},
        )
        
        return JsonResponse({'success': True, 'report_id': saved_report.id})
    
    return JsonResponse({'success': False}, status=400)


@login_required
@module_required('reports')
def saved_reports_list(request):
    """List all saved reports"""
    reports = SavedReport.objects.all()
    
    # Filter by type
    report_type = request.GET.get('type')
    if report_type:
        reports = reports.filter(report_type=report_type)
    
    context = {
        'reports': reports,
        'report_types': ReportTemplate.REPORT_TYPES,
        'selected_type': report_type,
    }
    return render(request, 'reports/saved_reports.html', context)


@login_required
@module_required('reports')
def view_saved_report(request, report_id):
    """View a previously saved report"""
    report = get_object_or_404(SavedReport, id=report_id)
    
    context = {
        'report': report,
    }
    return render(request, 'reports/view_saved_report.html', context)
