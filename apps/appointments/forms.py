from django import forms
from django.utils import timezone
from .models import Appointment, MedicalNote
from apps.doctors.models import DoctorProfile, DoctorAvailability

class AppointmentBookingForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        help_text="Select a date for your appointment"
    )
    time_slot = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        help_text="Select consultation start time (e.g. 09:00, 10:30)"
    )

    class Meta:
        model = Appointment
        fields = ('doctor', 'date', 'time_slot', 'reason')
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-select'}),
            'reason': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Describe your symptom or reason for consultation'}),
        }

    def __init__(self, *args, **kwargs):
        doctor_id = kwargs.pop('doctor_id', None)
        super().__init__(*args, **kwargs)
        if doctor_id:
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(pk=doctor_id, is_active=True)
            self.fields['doctor'].initial = doctor_id
        else:
            self.fields['doctor'].queryset = DoctorProfile.objects.filter(is_active=True)

    def clean_date(self):
        appointment_date = self.cleaned_data.get('date')
        if appointment_date and appointment_date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return appointment_date

    def clean(self):
        cleaned_data = super().clean()
        doctor = cleaned_data.get('doctor')
        date = cleaned_data.get('date')
        time_slot = cleaned_data.get('time_slot')

        if doctor and date and time_slot:
            # Check weekday availability of doctor
            weekday = date.weekday() # 0 = Monday ... 6 = Sunday
            availabilities = DoctorAvailability.objects.filter(doctor=doctor, day_of_week=weekday, is_available=True)
            
            if not availabilities.exists():
                day_name = dict(DoctorAvailability.DAYS_OF_WEEK).get(weekday)
                raise forms.ValidationError(f"Dr. {doctor.user.get_full_name() or doctor.user.username} is not available on {day_name}s.")

            slot_valid = False
            for avail in availabilities:
                if avail.start_time <= time_slot <= avail.end_time:
                    slot_valid = True
                    break

            if not slot_valid:
                raise forms.ValidationError(
                    f"Selected time slot ({time_slot.strftime('%H:%M')}) is outside doctor's available working hours on this day."
                )

            # Check double booking
            existing = Appointment.objects.filter(
                doctor=doctor,
                date=date,
                time_slot=time_slot
            ).exclude(status=Appointment.STATUS_CANCELLED)

            if existing.exists():
                raise forms.ValidationError(
                    f"Dr. {doctor.user.get_full_name() or doctor.user.username} is already booked for this exact time slot. Please choose another time."
                )

        return cleaned_data


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('status',)
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


class MedicalNoteForm(forms.ModelForm):
    class Meta:
        model = MedicalNote
        fields = ('diagnosis', 'prescription', 'doctor_notes')
        widgets = {
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Primary Diagnosis'}),
            'prescription': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Prescribed medications, dosage & duration'}),
            'doctor_notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Additional clinical notes'}),
        }
