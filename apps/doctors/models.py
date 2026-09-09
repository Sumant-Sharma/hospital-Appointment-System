from django.db import models
from apps.accounts.models import CustomUser

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_class = models.CharField(max_length=50, default='fa-stethoscope', help_text="FontAwesome icon CSS class")

    def __str__(self):
        return self.name

class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='doctors')
    specialization = models.CharField(max_length=150)
    qualification = models.CharField(max_length=150)
    experience_years = models.PositiveIntegerField(default=1)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='doctors/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def get_full_title(self):
        full_name = self.user.get_full_name()
        return f"Dr. {full_name}" if full_name else f"Dr. {self.user.username}"

    def __str__(self):
        return f"{self.get_full_title()} - {self.specialization}"

class DoctorAvailability(models.Model):
    DAYS_OF_WEEK = (
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    )

    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration_minutes = models.PositiveIntegerField(default=30)
    is_available = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Doctor Availabilities"
        ordering = ['day_of_week', 'start_time']

    def get_day_display_name(self):
        return dict(self.DAYS_OF_WEEK).get(self.day_of_week, '')

    def __str__(self):
        return f"{self.doctor.get_full_title()}: {self.get_day_display_name()} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"
