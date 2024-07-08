from django.urls import path
from . import views

urlpatterns = [
    path('share-patient-record/<int:patient_id>/', views.share_patient_record, name='share_patient_record'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
    path('create-treatment-plan/<int:patient_id>/', views.create_treatment_plan, name='create_treatment_plan'),
    path('create-referral/<int:patient_id>/', views.create_referral, name='create_referral'),
    path('list-shared-records/', views.list_shared_records, name='list_shared_records'),
]