from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import DoctorProfile, DoctorAvailability, Department
from .forms import DoctorProfileForm, DoctorAvailabilityForm, AdminCreateDoctorForm, DepartmentForm

def doctor_list(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    
    doctors = DoctorProfile.objects.filter(is_active=True).select_related('user', 'department')

    if query:
        doctors = doctors.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(qualification__icontains=query)
        )
    
    if department_id:
        doctors = doctors.filter(department_id=department_id)

    departments = Department.objects.all()

    return render(request, 'doctors/doctor_list.html', {
        'doctors': doctors,
        'departments': departments,
        'selected_department': department_id,
        'query': query
    })

def doctor_detail(request, pk):
    doctor = get_object_or_404(DoctorProfile.objects.select_related('user', 'department'), pk=pk)
    availabilities = doctor.availabilities.filter(is_available=True)
    
    return render(request, 'doctors/doctor_detail.html', {
        'doctor': doctor,
        'availabilities': availabilities
    })

@login_required
def manage_schedule(request):
    if not request.user.is_doctor:
        messages.error(request, "Only doctors can manage schedules.")
        return redirect('core:dashboard_redirect')
    
    doctor_profile = get_object_or_404(DoctorProfile, user=request.user)
    availabilities = doctor_profile.availabilities.all()

    if request.method == 'POST':
        form = DoctorAvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.doctor = doctor_profile
            availability.save()
            messages.success(request, "Working hours slot added successfully!")
            return redirect('doctors:manage_schedule')
    else:
        form = DoctorAvailabilityForm()

    return render(request, 'doctors/manage_schedule.html', {
        'form': form,
        'availabilities': availabilities,
        'doctor': doctor_profile
    })

@login_required
def delete_availability(request, pk):
    if not request.user.is_doctor:
        messages.error(request, "Unauthorized action.")
        return redirect('core:dashboard_redirect')
    
    availability = get_object_or_404(DoctorAvailability, pk=pk, doctor__user=request.user)
    availability.delete()
    messages.info(request, "Availability slot removed.")
    return redirect('doctors:manage_schedule')

@login_required
def create_doctor_by_admin(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to admins.")
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = AdminCreateDoctorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "New doctor registered successfully!")
            return redirect('core:admin_dashboard')
    else:
        form = AdminCreateDoctorForm()

    return render(request, 'doctors/create_doctor.html', {'form': form})

@login_required
def manage_departments(request):
    if not request.user.is_admin:
        messages.error(request, "Access restricted to admins.")
        return redirect('core:dashboard_redirect')

    departments = Department.objects.all()
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Department added successfully!")
            return redirect('doctors:manage_departments')
    else:
        form = DepartmentForm()

    return render(request, 'doctors/manage_departments.html', {
        'form': form,
        'departments': departments
    })
