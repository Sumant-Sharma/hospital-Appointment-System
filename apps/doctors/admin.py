from django.contrib import admin
from .models import Department, DoctorProfile, DoctorAvailability

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_full_title', 'department', 'specialization', 'experience_years', 'consultation_fee', 'is_active')
    list_filter = ('department', 'is_active')
    search_fields = ('user__first_name', 'user__last_name', 'specialization')

@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'day_of_week', 'start_time', 'end_time', 'is_available')
    list_filter = ('day_of_week', 'is_available')
