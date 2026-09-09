from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('<int:pk>/', views.doctor_detail, name='doctor_detail'),
    path('schedule/', views.manage_schedule, name='manage_schedule'),
    path('schedule/delete/<int:pk>/', views.delete_availability, name='delete_availability'),
    path('create/', views.create_doctor_by_admin, name='create_doctor'),
    path('departments/', views.manage_departments, name='manage_departments'),
]
