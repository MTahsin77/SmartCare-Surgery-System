from django.urls import path
from . import views

urlpatterns = [
    path('share-patient-record/', views.share_patient_record, name='share_patient_record'),
    path('shared-records/', views.shared_records_list, name='shared_records_list'),
]