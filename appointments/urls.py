from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_appointment, name='book_appointment'),
    path('reschedule/<int:appointment_id>/', views.reschedule_appointment, name='reschedule_appointment'),
    path('view/', views.view_appointments, name='view_appointments'),
    path('cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('detail/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('complete/<int:appointment_id>/', views.complete_appointment, name='complete_appointment'),
    path('issue-prescription/<int:appointment_id>/', views.issue_prescription, name='issue_prescription'),
    path('prescriptions/', views.view_prescriptions, name='view_prescriptions'),
    path('prescription/<int:prescription_id>/', views.prescription_detail, name='prescription_detail'),
    path('generate-invoice/<int:appointment_id>/', views.generate_invoice, name='generate_invoice'),
    path('view-invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('update-invoice/<int:invoice_id>/', views.update_invoice, name='update_invoice'),
    path('patient-invoices/', views.patient_invoices, name='patient_invoices'),
    path('list/', views.view_appointments, name='list_appointments'),
    path('admin-invoices/', views.admin_invoices, name='admin_invoices'),
    path('financial_reports/', views.financial_reports, name='financial_reports'),
    path('ajax/load-staff/', views.load_staff, name='load_staff'),
    path('ajax/get-available-slots/', views.get_available_slots, name='get_available_slots'),
    path('oauth2callback/', views.oauth2callback, name='oauth2callback'),
]
