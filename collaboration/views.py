from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SharedPatientRecord, Message, TreatmentPlan, Referral
from .forms import SharedPatientRecordForm, MessageForm, TreatmentPlanForm, ReferralForm
from django.contrib import messages
from .decorators import user_is_medical_staff
from django.core.mail import send_mail
from django.conf import settings
from .demo_data import DEMO_COLLABORATORS
from django.contrib.auth import get_user_model
from authentication.models import User, GPDetails
from authentication.decorators import user_is_doctor, user_is_nurse, user_is_admin
from django.template.loader import render_to_string
from appointments.models import Prescription

User = get_user_model()

@login_required
def share_patient_record(request, patient_id):
    try:
        patient = User.objects.get(id=patient_id, user_type='patient')
    except User.DoesNotExist:
        messages.error(request, f"Patient with ID {patient_id} does not exist.")
        return redirect('view_appointments')

    gps = GPDetails.objects.all()

    if request.method == 'POST':
        gp_id = request.POST.get('gp_id')
        try:
            gp = GPDetails.objects.get(id=gp_id)
        except GPDetails.DoesNotExist:
            messages.error(request, "Selected GP does not exist.")
            return render(request, 'collaboration/share_patient_record.html', {'gps': gps, 'patient': patient})

        prescriptions = Prescription.objects.filter(patient=patient)

        subject = 'Patient Record Sharing'
        message = render_to_string('collaboration/share_patient_record_email.html', {
            'gp': gp,
            'patient': patient,
            'prescriptions': prescriptions,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [gp.email])
        messages.success(request, f'Patient record shared with {gp.name} ({gp.email}).')
        return redirect('view_appointments')

    return render(request, 'collaboration/share_patient_record.html', {
        'gps': gps, 
        'patient': patient
    })

@login_required
@user_is_medical_staff
def send_message(request, receiver_id):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.receiver_id = receiver_id
            message.save()
            messages.success(request, 'Message sent successfully.')
            return redirect('inbox')
    else:
        form = MessageForm()
    return render(request, 'collaboration/send_message.html', {'form': form})

@login_required
@user_is_medical_staff
def create_treatment_plan(request, patient_id):
    if request.method == 'POST':
        form = TreatmentPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.patient_id = patient_id
            plan.created_by = request.user
            plan.save()
            form.save_m2m()
            messages.success(request, 'Treatment plan created successfully.')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = TreatmentPlanForm()
    return render(request, 'collaboration/create_treatment_plan.html', {'form': form})

@login_required
@user_is_medical_staff
def create_referral(request, patient_id):
    if request.method == 'POST':
        form = ReferralForm(request.POST)
        if form.is_valid():
            referral = form.save(commit=False)
            referral.patient_id = patient_id
            referral.referring_practitioner = request.user
            referral.save()
            messages.success(request, 'Referral created successfully.')
            return redirect('patient_detail', patient_id=patient_id)
    else:
        form = ReferralForm()
    return render(request, 'collaboration/create_referral.html', {'form': form})

@login_required
@user_is_medical_staff
def list_shared_records(request):
    shared_records = SharedPatientRecord.objects.filter(shared_with__contains=request.user.email)
    return render(request, 'collaboration/list_shared_records.html', {'shared_records': shared_records})