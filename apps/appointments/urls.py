from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('book/', views.book_appointment, name='book'),
    path('my-appointments/', views.my_appointments, name='my_appointments'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/update-status/', views.update_appointment_status, name='update_status'),
    path('<int:pk>/cancel/', views.cancel_appointment, name='cancel'),
    path('<int:pk>/medical-note/', views.add_medical_note, name='add_medical_note'),
    path('api/slots/<int:doctor_id>/<str:date_str>/', views.get_available_slots_api, name='api_slots'),
]
