from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import SchoolYear, Program, Grade, Section, FeeStructure, VATConfig
from .forms import SchoolYearForm, ProgramForm, GradeForm, SectionForm, FeeStructureForm, VATConfigForm

# Create your views here.

@login_required
def settings_dashboard(request):
    """Settings module dashboard showing all configuration options"""
    context = {
        'school_years_count': SchoolYear.objects.count(),
        'active_school_year': SchoolYear.objects.filter(is_active=True).first(),
        'programs_count': Program.objects.filter(is_active=True).count(),
        'grades_count': Grade.objects.filter(is_active=True).count(),
        'sections_count': Section.objects.filter(is_active=True).count(),
        'fee_structures_count': FeeStructure.objects.filter(is_active=True).count(),
        'active_vat': VATConfig.objects.filter(is_active=True).first(),
    }
    return render(request, 'settings_app/dashboard.html', context)


# ==================== School Year Views ====================

@login_required
def school_year_list(request):
    """List all school years"""
    school_years = SchoolYear.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        school_years = school_years.filter(
            Q(name__icontains=search_query)
        )
    
    context = {
        'school_years': school_years,
        'search_query': search_query,
    }
    return render(request, 'settings_app/school_year_list.html', context)


@login_required
def school_year_create(request):
    """Create a new school year"""
    if request.method == 'POST':
        form = SchoolYearForm(request.POST)
        if form.is_valid():
            school_year = form.save()
            messages.success(request, f'School year "{school_year.name}" created successfully!')
            return redirect('settings_app:school_year_list')
    else:
        form = SchoolYearForm()
    
    return render(request, 'settings_app/school_year_form.html', {'form': form, 'action': 'Create'})


@login_required
def school_year_edit(request, pk):
    """Edit an existing school year"""
    school_year = get_object_or_404(SchoolYear, pk=pk)
    
    if request.method == 'POST':
        form = SchoolYearForm(request.POST, instance=school_year)
        if form.is_valid():
            form.save()
            messages.success(request, f'School year "{school_year.name}" updated successfully!')
            return redirect('settings_app:school_year_list')
    else:
        form = SchoolYearForm(instance=school_year)
    
    return render(request, 'settings_app/school_year_form.html', {'form': form, 'action': 'Edit', 'school_year': school_year})


@login_required
def school_year_delete(request, pk):
    """Delete a school year"""
    school_year = get_object_or_404(SchoolYear, pk=pk)
    
    if request.method == 'POST':
        name = school_year.name
        school_year.delete()
        messages.success(request, f'School year "{name}" deleted successfully!')
        return redirect('settings_app:school_year_list')
    
    return render(request, 'settings_app/school_year_confirm_delete.html', {'school_year': school_year})


# ==================== Program Views ====================

@login_required
def program_list(request):
    """List all programs"""
    programs = Program.objects.all()
    
    search_query = request.GET.get('search', '')
    if search_query:
        programs = programs.filter(
            Q(name__icontains=search_query) | Q(code__icontains=search_query)
        )
    
    context = {
        'programs': programs,
        'search_query': search_query,
    }
    return render(request, 'settings_app/program_list.html', context)


@login_required
def program_create(request):
    """Create a new program"""
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            program = form.save()
            messages.success(request, f'Program "{program.name}" created successfully!')
            return redirect('settings_app:program_list')
    else:
        form = ProgramForm()
    
    return render(request, 'settings_app/program_form.html', {'form': form, 'action': 'Create'})


@login_required
def program_edit(request, pk):
    """Edit an existing program"""
    program = get_object_or_404(Program, pk=pk)
    
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, f'Program "{program.name}" updated successfully!')
            return redirect('settings_app:program_list')
    else:
        form = ProgramForm(instance=program)
    
    return render(request, 'settings_app/program_form.html', {'form': form, 'action': 'Edit', 'program': program})


# ==================== Grade Views ====================

@login_required
def grade_list(request):
    """List all grades"""
    grades = Grade.objects.select_related('program').all()
    
    # Filter by program
    program_id = request.GET.get('program', '')
    if program_id:
        grades = grades.filter(program_id=program_id)
    
    programs = Program.objects.filter(is_active=True)
    
    context = {
        'grades': grades,
        'programs': programs,
        'selected_program': program_id,
    }
    return render(request, 'settings_app/grade_list.html', context)


@login_required
def grade_create(request):
    """Create a new grade"""
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save()
            messages.success(request, f'Grade "{grade.name}" created successfully!')
            return redirect('settings_app:grade_list')
    else:
        form = GradeForm()
    
    return render(request, 'settings_app/grade_form.html', {'form': form, 'action': 'Create'})


@login_required
def grade_edit(request, pk):
    """Edit an existing grade"""
    grade = get_object_or_404(Grade, pk=pk)
    
    if request.method == 'POST':
        form = GradeForm(request.POST, instance=grade)
        if form.is_valid():
            form.save()
            messages.success(request, f'Grade "{grade.name}" updated successfully!')
            return redirect('settings_app:grade_list')
    else:
        form = GradeForm(instance=grade)
    
    return render(request, 'settings_app/grade_form.html', {'form': form, 'action': 'Edit', 'grade': grade})


# ==================== Section Views ====================

@login_required
def section_list(request):
    """List all sections"""
    sections = Section.objects.select_related('grade__program').all()
    
    # Filter by grade
    grade_id = request.GET.get('grade', '')
    if grade_id:
        sections = sections.filter(grade_id=grade_id)
    
    grades = Grade.objects.filter(is_active=True).select_related('program')
    
    context = {
        'sections': sections,
        'grades': grades,
        'selected_grade': grade_id,
    }
    return render(request, 'settings_app/section_list.html', context)


@login_required
def section_create(request):
    """Create a new section"""
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():
            section = form.save()
            messages.success(request, f'Section "{section}" created successfully!')
            return redirect('settings_app:section_list')
    else:
        form = SectionForm()
    
    return render(request, 'settings_app/section_form.html', {'form': form, 'action': 'Create'})


@login_required
def section_edit(request, pk):
    """Edit an existing section"""
    section = get_object_or_404(Section, pk=pk)
    
    if request.method == 'POST':
        form = SectionForm(request.POST, instance=section)
        if form.is_valid():
            form.save()
            messages.success(request, f'Section "{section}" updated successfully!')
            return redirect('settings_app:section_list')
    else:
        form = SectionForm(instance=section)
    
    return render(request, 'settings_app/section_form.html', {'form': form, 'action': 'Edit', 'section': section})


# ==================== Fee Structure Views ====================

@login_required
def fee_structure_list(request):
    """List all fee structures"""
    fee_structures = FeeStructure.objects.select_related('program', 'grade').all()
    
    # Filters
    program_id = request.GET.get('program', '')
    if program_id:
        fee_structures = fee_structures.filter(program_id=program_id)
    
    fee_type = request.GET.get('fee_type', '')
    if fee_type:
        fee_structures = fee_structures.filter(fee_type=fee_type)
    
    programs = Program.objects.filter(is_active=True)
    fee_types = FeeStructure.FEE_TYPE_CHOICES
    
    context = {
        'fee_structures': fee_structures,
        'programs': programs,
        'fee_types': fee_types,
        'selected_program': program_id,
        'selected_fee_type': fee_type,
    }
    return render(request, 'settings_app/fee_structure_list.html', context)


@login_required
def fee_structure_create(request):
    """Create a new fee structure"""
    if request.method == 'POST':
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            fee_structure = form.save()
            messages.success(request, f'Fee structure "{fee_structure.name}" created successfully!')
            return redirect('settings_app:fee_structure_list')
    else:
        form = FeeStructureForm()
    
    return render(request, 'settings_app/fee_structure_form.html', {'form': form, 'action': 'Create'})


@login_required
def fee_structure_edit(request, pk):
    """Edit an existing fee structure"""
    fee_structure = get_object_or_404(FeeStructure, pk=pk)
    
    if request.method == 'POST':
        form = FeeStructureForm(request.POST, instance=fee_structure)
        if form.is_valid():
            form.save()
            messages.success(request, f'Fee structure "{fee_structure.name}" updated successfully!')
            return redirect('settings_app:fee_structure_list')
    else:
        form = FeeStructureForm(instance=fee_structure)
    
    return render(request, 'settings_app/fee_structure_form.html', {'form': form, 'action': 'Edit', 'fee_structure': fee_structure})


# ==================== VAT Config Views ====================

@login_required
def vat_config_list(request):
    """List all VAT configurations"""
    vat_configs = VATConfig.objects.all()
    
    context = {
        'vat_configs': vat_configs,
    }
    return render(request, 'settings_app/vat_config_list.html', context)


@login_required
def vat_config_create(request):
    """Create a new VAT configuration"""
    if request.method == 'POST':
        form = VATConfigForm(request.POST)
        if form.is_valid():
            vat_config = form.save()
            messages.success(request, f'VAT configuration created successfully!')
            return redirect('settings_app:vat_config_list')
    else:
        form = VATConfigForm()
    
    return render(request, 'settings_app/vat_config_form.html', {'form': form, 'action': 'Create'})


@login_required
def vat_config_edit(request, pk):
    """Edit an existing VAT configuration"""
    vat_config = get_object_or_404(VATConfig, pk=pk)
    
    if request.method == 'POST':
        form = VATConfigForm(request.POST, instance=vat_config)
        if form.is_valid():
            form.save()
            messages.success(request, 'VAT configuration updated successfully!')
            return redirect('settings_app:vat_config_list')
    else:
        form = VATConfigForm(instance=vat_config)
    
    return render(request, 'settings_app/vat_config_form.html', {'form': form, 'action': 'Edit', 'vat_config': vat_config})
