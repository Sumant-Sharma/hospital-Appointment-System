from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from datetime import datetime, timedelta

from .models import Appointment, MedicalNote
from .forms import AppointmentBookingForm, AppointmentStatusForm, MedicalNoteForm
from apps.doctors.models import DoctorProfile, DoctorAvailability
from apps.accounts.models import PatientProfile

@login_required
def book_appointment(request):
    if not request.user.is_patient:
        messages.error(request, "Only registered patients can book appointments.")
        return redirect('core:dashboard_redirect')

    patient_profile, _ = PatientProfile.objects.get_or_create(user=request.user)
    doctor_id = request.GET.get('doctor')

    if request.method == 'POST':
        form = AppointmentBookingForm(request.POST, doctor_id=doctor_id)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient_profile
            appointment.status = Appointment.STATUS_PENDING
            appointment.save()

            # Trigger Email notification
            try:
                subject = f"Appointment Booked - #{appointment.id}"
                message = (
                    f"Hello {request.user.get_full_name() or request.user.username},\n\n"
                    f"Your appointment with {appointment.doctor.get_full_title()} is successfully booked.\n"
                    f"Date: {appointment.date}\n"
                    f"Time: {appointment.time_slot.strftime('%H:%M')}\n"
                    f"Status: Pending Confirmation\n\n"
                    f"Thank you for choosing our Hospital System."
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f"Appointment successfully booked for {appointment.date} at {appointment.time_slot.strftime('%H:%M')}! Status: Pending.")
            return redirect('appointments:my_appointments')
    else:
        form = AppointmentBookingForm(doctor_id=doctor_id)

    selected_doctor = DoctorProfile.objects.filter(pk=doctor_id).first() if doctor_id else None

    return render(request, 'appointments/book.html', {
        'form': form,
        'selected_doctor': selected_doctor
    })

@login_required
def my_appointments(request):
    user = request.user
    if user.is_patient:
        patient_profile = get_object_or_404(PatientProfile, user=user)
        appointments = Appointment.objects.filter(patient=patient_profile).select_related('doctor__user', 'doctor__department')
    elif user.is_doctor:
        doctor_profile = get_object_or_404(DoctorProfile, user=user)
        appointments = Appointment.objects.filter(doctor=doctor_profile).select_related('patient__user')
    elif user.is_admin:
        appointments = Appointment.objects.all().select_related('doctor__user', 'patient__user', 'doctor__department')
    else:
        appointments = Appointment.objects.none()

    status_filter = request.GET.get('status')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    return render(request, 'appointments/my_appointments.html', {
        'appointments': appointments,
        'selected_status': status_filter
    })

@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment.objects.select_related('doctor__user', 'patient__user', 'doctor__department'), pk=pk)
    user = request.user

    # Access control
    if not (user.is_admin or (user.is_doctor and appointment.doctor.user == user) or (user.is_patient and appointment.patient.user == user)):
        messages.error(request, "You do not have permission to view this appointment.")
        return redirect('core:dashboard_redirect')

    medical_note = getattr(appointment, 'medical_note', None)
    status_form = AppointmentStatusForm(instance=appointment) if (user.is_doctor or user.is_admin) else None
    note_form = MedicalNoteForm(instance=medical_note) if (user.is_doctor and appointment.doctor.user == user) else None

    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'medical_note': medical_note,
        'status_form': status_form,
        'note_form': note_form,
    })

@login_required
def update_appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    if not (user.is_admin or (user.is_doctor and appointment.doctor.user == user)):
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard_redirect')

    if request.method == 'POST':
        form = AppointmentStatusForm(request.POST, instance=appointment)
        if form.is_valid():
            old_status = appointment.status
            updated_appointment = form.save()

            # Email notification on status update
            try:
                subject = f"Appointment Status Updated - #{updated_appointment.id}"
                message = (
                    f"Hello {updated_appointment.patient.user.get_full_name() or updated_appointment.patient.user.username},\n\n"
                    f"Your appointment with {updated_appointment.doctor.get_full_title()} on {updated_appointment.date} has been updated.\n"
                    f"New Status: {updated_appointment.get_status_display()}\n\n"
                    f"Thank you."
                )
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [updated_appointment.patient.user.email],
                    fail_silently=True,
                )
            except Exception:
                pass

            messages.success(request, f"Appointment status changed from {old_status.upper()} to {updated_appointment.status.upper()}.")

    return redirect('appointments:appointment_detail', pk=pk)

@login_required
def cancel_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    user = request.user

    if not (user.is_admin or (user.is_doctor and appointment.doctor.user == user) or (user.is_patient and appointment.patient.user == user)):
        messages.error(request, "Permission denied.")
        return redirect('core:dashboard_redirect')

    if appointment.status == Appointment.STATUS_COMPLETED:
        messages.error(request, "Completed appointments cannot be cancelled.")
        return redirect('appointments:appointment_detail', pk=pk)

    appointment.status = Appointment.STATUS_CANCELLED
    appointment.save()

    messages.info(request, f"Appointment #{appointment.id} has been cancelled.")
    return redirect('appointments:my_appointments')

@login_required
def add_medical_note(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if not (request.user.is_doctor and appointment.doctor.user == request.user):
        messages.error(request, "Only the assigned doctor can write medical notes.")
        return redirect('core:dashboard_redirect')

    medical_note = getattr(appointment, 'medical_note', None)

    if request.method == 'POST':
        form = MedicalNoteForm(request.POST, instance=medical_note)
        if form.is_valid():
            note = form.save(commit=False)
            note.appointment = appointment
            note.save()
            messages.success(request, "Medical note saved successfully!")
            return redirect('appointments:appointment_detail', pk=pk)

    return redirect('appointments:appointment_detail', pk=pk)

def get_available_slots_api(request, doctor_id, date_str):
    """API endpoint returning available timeslots for a doctor on a given date YYYY-MM-DD"""
    try:
        booking_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)

    weekday = booking_date.weekday()
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)
    availabilities = DoctorAvailability.objects.filter(doctor=doctor, day_of_week=weekday, is_available=True)

    if not availabilities.exists():
        return JsonResponse({'available_slots': [], 'message': 'Doctor is not available on this day.'})

    booked_slots = set(
        Appointment.objects.filter(doctor=doctor, date=booking_date)
        .exclude(status=Appointment.STATUS_CANCELLED)
        .values_list('time_slot', flat=True)
    )

    slots = []
    for avail in availabilities:
        current_dt = datetime.combine(booking_date, avail.start_time)
        end_dt = datetime.combine(booking_date, avail.end_time)
        slot_delta = timedelta(minutes=avail.slot_duration_minutes)

        while current_dt + slot_delta <= end_dt:
            slot_time = current_dt.time()
            is_booked = slot_time in booked_slots
            slots.append({
                'time': slot_time.strftime('%H:%M'),
                'display': slot_time.strftime('%I:%M %p'),
                'is_booked': is_booked
            })
            current_dt += slot_delta

    return JsonResponse({'available_slots': slots})
