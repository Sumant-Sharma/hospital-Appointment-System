from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, time, timedelta

from apps.accounts.models import CustomUser, PatientProfile
from apps.doctors.models import Department, DoctorProfile, DoctorAvailability
from apps.appointments.models import Appointment, MedicalNote

class Command(BaseCommand):
    help = "Seeds initial sample data for departments, doctors, patients, schedules, and appointments."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting database seed process..."))

        # 1. Admin User
        admin_user, created = CustomUser.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@hospital.com",
                "first_name": "System",
                "last_name": "Admin",
                "role": CustomUser.ROLE_ADMIN,
                "is_staff": True,
                "is_superuser": True
            }
        )
        if created:
            admin_user.set_password("admin123")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created Superuser / Admin: admin / admin123"))

        # 2. Departments
        departments_data = [
            ("Cardiology", "Heart, vascular, and cardiac care specialists", "fa-heart-pulse"),
            ("Neurology", "Brain, spine, and nervous system disorders", "fa-brain"),
            ("Orthopedics", "Bone, joint, muscle, and ligament reconstruction", "fa-bone"),
            ("Pediatrics", "Comprehensive medical care for infants, children, and teens", "fa-child-reaching"),
            ("Dermatology", "Skin, hair, and cosmetic dermatology care", "fa-user-doctor"),
            ("General Medicine", "Primary healthcare, routine wellness, and diagnostic medicine", "fa-stethoscope"),
        ]

        depts = {}
        for name, desc, icon in departments_data:
            dept, _ = Department.objects.get_or_create(
                name=name,
                defaults={"description": desc, "icon_class": icon}
            )
            depts[name] = dept
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(depts)} departments."))

        # 3. Doctors
        doctors_info = [
            {
                "username": "dr_smith",
                "email": "smith@hospital.com",
                "first_name": "Robert",
                "last_name": "Smith",
                "department": depts["Cardiology"],
                "specialization": "Interventional Cardiology",
                "qualification": "MD, FACC, Board Certified Cardiologist",
                "experience_years": 14,
                "consultation_fee": 120.00,
                "bio": "Specialist in cardiovascular wellness, angioplasty, and preventative cardiology with over 14 years of practice."
            },
            {
                "username": "dr_jones",
                "email": "jones@hospital.com",
                "first_name": "Emily",
                "last_name": "Jones",
                "department": depts["Neurology"],
                "specialization": "Clinical Neurophysiology & Epilepsy",
                "qualification": "MD, PhD Neurological Sciences",
                "experience_years": 10,
                "consultation_fee": 150.00,
                "bio": "Focuses on migraine management, stroke recovery, and advanced neurological diagnostics."
            },
            {
                "username": "dr_taylor",
                "email": "taylor@hospital.com",
                "first_name": "David",
                "last_name": "Taylor",
                "department": depts["Pediatrics"],
                "specialization": "General Pediatrics & Neonatology",
                "qualification": "MBBS, DCH, FAAP",
                "experience_years": 8,
                "consultation_fee": 90.00,
                "bio": "Dedicated pediatric specialist passionate about child growth, vaccinations, and adolescent wellness."
            },
            {
                "username": "dr_adams",
                "email": "adams@hospital.com",
                "first_name": "Sarah",
                "last_name": "Adams",
                "department": depts["Orthopedics"],
                "specialization": "Sports Medicine & Joint Replacement",
                "qualification": "MS Orthopedics, FRCS",
                "experience_years": 12,
                "consultation_fee": 130.00,
                "bio": "Expert orthopedist specializing in minimally invasive knee and shoulder arthroscopy."
            },
        ]

        doctor_profiles = []
        for doc in doctors_info:
            user, u_created = CustomUser.objects.get_or_create(
                username=doc["username"],
                defaults={
                    "email": doc["email"],
                    "first_name": doc["first_name"],
                    "last_name": doc["last_name"],
                    "role": CustomUser.ROLE_DOCTOR,
                    "phone": "+1 555-0199"
                }
            )
            if u_created:
                user.set_password("doctor123")
                user.save()

            profile, _ = DoctorProfile.objects.get_or_create(
                user=user,
                defaults={
                    "department": doc["department"],
                    "specialization": doc["specialization"],
                    "qualification": doc["qualification"],
                    "experience_years": doc["experience_years"],
                    "consultation_fee": doc["consultation_fee"],
                    "bio": doc["bio"]
                }
            )
            doctor_profiles.append(profile)

            # Seed Availabilities (Mon - Fri, 09:00 - 17:00)
            for day in range(0, 5): # Mon to Fri
                DoctorAvailability.objects.get_or_create(
                    doctor=profile,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(17, 0),
                    defaults={"slot_duration_minutes": 30, "is_available": True}
                )

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(doctor_profiles)} doctor profiles with weekly availability schedules. Password: doctor123"))

        # 4. Patients
        patients_info = [
            {"username": "patient_john", "email": "john@example.com", "first_name": "John", "last_name": "Doe", "blood": "O+", "phone": "+1 555-0101"},
            {"username": "patient_sarah", "email": "sarah@example.com", "first_name": "Sarah", "last_name": "Connor", "blood": "A+", "phone": "+1 555-0102"},
            {"username": "patient_mike", "email": "mike@example.com", "first_name": "Mike", "last_name": "Ross", "blood": "B-", "phone": "+1 555-0103"},
        ]

        patient_profiles = []
        for pat in patients_info:
            user, u_created = CustomUser.objects.get_or_create(
                username=pat["username"],
                defaults={
                    "email": pat["email"],
                    "first_name": pat["first_name"],
                    "last_name": pat["last_name"],
                    "role": CustomUser.ROLE_PATIENT,
                    "phone": pat["phone"]
                }
            )
            if u_created:
                user.set_password("patient123")
                user.save()

            profile, _ = PatientProfile.objects.get_or_create(
                user=user,
                defaults={
                    "blood_group": pat["blood"],
                    "address": "123 Medical Center Way, Suite 400",
                    "emergency_contact": "+1 555-9999"
                }
            )
            patient_profiles.append(profile)

        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patient_profiles)} patient profiles. Password: patient123"))

        # 5. Sample Appointments
        today = date.today()
        # Find next Monday/Tuesday
        next_monday = today + timedelta(days=(7 - today.weekday()) % 7 or 7)
        next_tuesday = next_monday + timedelta(days=1)
        next_wednesday = next_monday + timedelta(days=2)

        sample_appointments = [
            {
                "patient": patient_profiles[0],
                "doctor": doctor_profiles[0], # Dr. Smith (Cardiology)
                "date": next_monday,
                "time_slot": time(10, 0),
                "status": Appointment.STATUS_CONFIRMED,
                "reason": "Routine cardiac checkup and hypertension review."
            },
            {
                "patient": patient_profiles[1],
                "doctor": doctor_profiles[1], # Dr. Jones (Neurology)
                "date": next_tuesday,
                "time_slot": time(11, 30),
                "status": Appointment.STATUS_PENDING,
                "reason": "Frequent severe headaches and migraine assessment."
            },
            {
                "patient": patient_profiles[2],
                "doctor": doctor_profiles[2], # Dr. Taylor (Pediatrics)
                "date": next_wednesday,
                "time_slot": time(14, 0),
                "status": Appointment.STATUS_COMPLETED,
                "reason": "Annual child wellness exam and vaccination."
            },
        ]

        for appt_data in sample_appointments:
            appt, created = Appointment.objects.get_or_create(
                patient=appt_data["patient"],
                doctor=appt_data["doctor"],
                date=appt_data["date"],
                time_slot=appt_data["time_slot"],
                defaults={
                    "status": appt_data["status"],
                    "reason": appt_data["reason"]
                }
            )
            if created and appt.status == Appointment.STATUS_COMPLETED:
                MedicalNote.objects.create(
                    appointment=appt,
                    diagnosis="Mild pediatric seasonal allergies",
                    prescription="Cetirizine Syrup 5ml once daily before bed for 7 days.",
                    doctor_notes="Patient is growing healthy in 75th percentile height/weight."
                )

        self.stdout.write(self.style.SUCCESS("Sample appointments & medical records seeded successfully!"))
        self.stdout.write(self.style.SUCCESS("All seed data created cleanly."))
