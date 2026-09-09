# CarePulse Hospital Appointment System

A production-quality Django Hospital Appointment System with custom user roles (Admin, Doctor, Patient), doctor availability scheduling, anti-double booking appointment management, clinical medical records, and responsive Bootstrap 5 dashboards.

## Features

- **Role-Based Authentication & Redirection**: Custom User model (`accounts.CustomUser`) with distinct permissions and dynamic post-login dashboards for **Admin**, **Doctor**, and **Patient**.
- **Specialist Directory & Search**: Filter doctors by clinical department, name, specialization, or fee.
- **Doctor Availability Management**: Doctors can set weekly working days, consultation hours, and slot duration.
- **Smart Appointment Booking**: Live availability slot lookup API, date/time validation, and strict prevention of double bookings.
- **Medical Records**: Doctors can record diagnoses, prescriptions, and notes for consultations.
- **Seed Data Command**: Single command to generate admin, departments, doctor accounts, patient accounts, availability schedules, and sample appointments.

---

## Quickstart Guide

### 1. Requirements & Virtual Environment

Ensure Python 3.9+ is installed.

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 4. Populate Sample Seed Data

Run the custom seed data management command to populate initial admin, departments, doctor accounts, patient accounts, schedules, and appointments:

```bash
python manage.py seed_data
```

#### Seeded Credentials:
- **Admin**: `admin` / `admin123`
- **Doctor (Cardiology)**: `dr_smith` / `doctor123`
- **Doctor (Neurology)**: `dr_jones` / `doctor123`
- **Doctor (Pediatrics)**: `dr_taylor` / `doctor123`
- **Doctor (Orthopedics)**: `dr_adams` / `doctor123`
- **Patient**: `patient_john` / `patient123`
- **Patient**: `patient_sarah` / `patient123`

### 5. Start Development Server

```bash
python manage.py runserver 8000
```

Open your browser at `http://127.0.0.1:8000/`.

---

## Project Structure

```text
django_hospital/
├── manage.py
├── requirements.txt
├── README.md
├── hospital_project/       # Root project configuration & settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/           # CustomUser, PatientProfile, Auth & Login views
│   ├── doctors/            # Department, DoctorProfile, DoctorAvailability views & forms
│   ├── appointments/       # Appointment, MedicalNote, Booking Logic & Seed Command
│   └── core/               # Public Home landing page & Role Dashboards
├── templates/              # Bootstrap 5 styled templates
│   ├── base.html
│   ├── home.html
│   ├── accounts/
│   ├── dashboards/
│   ├── doctors/
│   └── appointments/
└── static/                 # Custom CSS & JS styling
```

---

## Technical Configuration Notes

- **Database**: Uses SQLite for zero-config local development, with automatic fallback for PostgreSQL via `DATABASE_URL` standard in `settings.py`.
- **Email Notifications**: Configured to use Django console backend (`django.core.mail.backends.console.EmailBackend`) during development so booking/status change emails print directly to the terminal.
