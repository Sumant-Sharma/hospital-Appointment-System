from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.utils import timezone

from apps.accounts.models import CustomUser, PatientProfile
from apps.doctors.models import DoctorProfile, Department
from apps.appointments.models import Appointment

def home(request):
    if request.user.is_authenticated:
        return redirect('core:dashboard_redirect')

    departments = Department.objects.annotate(doctor_count=Count('doctors')).all()[:6]
    doctors = DoctorProfile.objects.filter(is_active=True).select_related('user', 'department')[:4]
    
    stats = {
        'total_doctors': DoctorProfile.objects.filter(is_active=True).count(),
        'total_patients': PatientProfile.objects.count(),
        'total_departments': Department.objects.count(),
        'total_appointments': Appointment.objects.count(),
    }

    return render(request, 'home.html', {
        'departments': departments,
        'doctors': doctors,
        'stats': stats
    })

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin:
        return redirect('core:admin_dashboard')
    elif user.is_doctor:
        return redirect('core:doctor_dashboard')
    elif user.is_patient:
        return redirect('core:patient_dashboard')
    else:
        return redirect('core:home')

@login_required
def admin_dashboard(request):
    if not request.user.is_admin:
        messages.error(request, "Unauthorized access to Admin Dashboard.")
        return redirect('core:dashboard_redirect')

    total_doctors = DoctorProfile.objects.filter(is_active=True).count()
    total_patients = PatientProfile.objects.count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status=Appointment.STATUS_PENDING).count()
    confirmed_appointments = Appointment.objects.filter(status=Appointment.STATUS_CONFIRMED).count()
    completed_appointments = Appointment.objects.filter(status=Appointment.STATUS_COMPLETED).count()

    recent_appointments = Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__department').all()[:10]
    doctors = DoctorProfile.objects.select_related('user', 'department').all()

    return render(request, 'dashboards/admin_dashboard.html', {
        'total_doctors': total_doctors,
        'total_patients': total_patients,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'confirmed_appointments': confirmed_appointments,
        'completed_appointments': completed_appointments,
        'recent_appointments': recent_appointments,
        'doctors': doctors
    })

@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor:
        messages.error(request, "Unauthorized access to Doctor Dashboard.")
        return redirect('core:dashboard_redirect')

    doctor_profile = getattr(request.user, 'doctor_profile', None)
    if not doctor_profile:
        messages.error(request, "Doctor profile record not found.")
        return redirect('core:home')

    today = timezone.now().date()
    today_appointments = Appointment.objects.filter(doctor=doctor_profile, date=today).select_related('patient__user')
    upcoming_appointments = Appointment.objects.filter(doctor=doctor_profile, date__gt=today).exclude(status=Appointment.STATUS_CANCELLED).select_related('patient__user')
    
    total_patients_treated = Appointment.objects.filter(doctor=doctor_profile, status=Appointment.STATUS_COMPLETED).values('patient').distinct().count()
    pending_count = Appointment.objects.filter(doctor=doctor_profile, status=Appointment.STATUS_PENDING).count()

    return render(request, 'dashboards/doctor_dashboard.html', {
        'doctor': doctor_profile,
        'today_appointments': today_appointments,
        'upcoming_appointments': upcoming_appointments,
        'total_patients_treated': total_patients_treated,
        'pending_count': pending_count,
        'today_date': today
    })

@login_required
def patient_dashboard(request):
    if not request.user.is_patient:
        messages.error(request, "Unauthorized access to Patient Dashboard.")
        return redirect('core:dashboard_redirect')

    patient_profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    
    today = timezone.now().date()
    upcoming_appointments = Appointment.objects.filter(
        patient=patient_profile,
        date__gte=today
    ).exclude(status=Appointment.STATUS_CANCELLED).select_related('doctor__user', 'doctor__department')

    past_appointments = Appointment.objects.filter(
        patient=patient_profile,
        date__lt=today
    ).select_related('doctor__user', 'doctor__department')

    departments = Department.objects.all()

    return render(request, 'dashboards/patient_dashboard.html', {
        'patient': patient_profile,
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments,
        'departments': departments
    })
