from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse/', views.nurse_dashboard, name='nurse_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage-appointments/', views.manage_appointments, name='manage_appointments'),
]
