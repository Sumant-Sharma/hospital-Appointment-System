from django.db import models
from django.core.exceptions import ValidationError
from apps.accounts.models import PatientProfile
from apps.doctors.models import DoctorProfile

class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'

    STATUS_CHOICES = (
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    )

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    date = models.DateField()
    time_slot = models.TimeField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time_slot']

    def clean(self):
        super().clean()
        # Prevent double booking for active appointments
        existing = Appointment.objects.filter(
            doctor=self.doctor,
            date=self.date,
            time_slot=self.time_slot
        ).exclude(status=self.STATUS_CANCELLED)

        if self.pk:
            existing = existing.exclude(pk=self.pk)

        if existing.exists():
            raise ValidationError(
                f"Doctor {self.doctor.get_full_title()} already has an appointment booked for {self.date} at {self.time_slot.strftime('%H:%M')}."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment #{self.id}: {self.patient.user.get_full_name()} with {self.doctor.get_full_title()} on {self.date} @ {self.time_slot.strftime('%H:%M')} [{self.get_status_display()}]"


class MedicalNote(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='medical_note')
    diagnosis = models.TextField()
    prescription = models.TextField(blank=True, null=True)
    doctor_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Medical Record for Appointment #{self.appointment.id}"
