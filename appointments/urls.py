from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('view/', views.view_appointments, name='view_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('ajax/load-staff/', views.load_staff, name='ajax_load_staff'),
    path('issue-prescription/<int:appointment_id>/', views.issue_prescription, name='issue_prescription'),
    path('prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('prescription/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    path('appointment/<int:appointment_id>/issue_prescription/', views.issue_prescription, name='issue_prescription'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('ajax/get-available-slots/', views.get_available_slots, name='get_available_slots'),
]
