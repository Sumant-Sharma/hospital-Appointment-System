from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import date, time
from apps.accounts.models import CustomUser, PatientProfile
from apps.doctors.models import Department, DoctorProfile, DoctorAvailability
from apps.appointments.models import Appointment

class AppointmentBookingTestCase(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name="Cardiology")
        self.doc_user = CustomUser.objects.create_user(
            username="test_doctor",
            password="pass123",
            role=CustomUser.ROLE_DOCTOR,
            first_name="Alice",
            last_name="Smith"
        )
        self.doctor = DoctorProfile.objects.create(
            user=self.doc_user,
            department=self.dept,
            specialization="Heart Surgery",
            qualification="MD",
            consultation_fee=100.00
        )
        # Mon (0) availability
        DoctorAvailability.objects.create(
            doctor=self.doctor,
            day_of_week=0,
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        self.pat_user = CustomUser.objects.create_user(
            username="test_patient",
            password="pass123",
            role=CustomUser.ROLE_PATIENT,
            first_name="Bob",
            last_name="Jones"
        )
        self.patient = PatientProfile.objects.create(user=self.pat_user)

    def test_successful_appointment(self):
        appt = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2026, 8, 10), # Monday
            time_slot=time(10, 0),
            reason="Checkup"
        )
        self.assertEqual(appt.status, Appointment.STATUS_PENDING)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_double_booking_prevention(self):
        # Create initial appointment
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2026, 8, 10),
            time_slot=time(10, 0),
            reason="Checkup 1"
        )

        # Attempt to create duplicate appointment for same doctor, date, slot
        duplicate_appt = Appointment(
            patient=self.patient,
            doctor=self.doctor,
            date=date(2026, 8, 10),
            time_slot=time(10, 0),
            reason="Checkup 2"
        )
        with self.assertRaises(ValidationError):
            duplicate_appt.full_clean()
