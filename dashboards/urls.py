from django.urls import path
from . import views

urlpatterns = [
    path('patient/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor/', views.doctor_dashboard, name='doctor_dashboard'),
    path('nurse/', views.nurse_dashboard, name='nurse_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
    path('approve_doctors/', views.approve_doctors, name='approve_doctors'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('manage_appointments/', views.manage_appointments, name='manage_appointments'),
    path('issue_prescription/<int:appointment_id>/', views.issue_prescription, name='issue_prescription'),
]
