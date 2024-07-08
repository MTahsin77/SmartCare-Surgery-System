from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .calendar_service import create_flow, get_calendar_service
from .forms import AppointmentForm, PrescriptionForm, InvoiceForm
from .models import Appointment, Prescription, Invoice
from authentication.decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin
from authentication.models import User 
from django.utils import timezone
from google.auth.exceptions import RefreshError
from django.db import transaction
from django.db.models import Sum
from decimal import Decimal
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from math import radians, cos, sin, asin, sqrt
import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from authentication.models import GPDetails, User

logger = logging.getLogger(__name__)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        logger.info(f"POST data: {request.POST}")
        if form.is_valid():
            logger.info("Form is valid")
            try:
                appointment = form.save(commit=False)
                appointment.patient = request.user
                appointment.latitude = form.cleaned_data.get('latitude')
                appointment.longitude = form.cleaned_data.get('longitude')
                logger.info(f"Appointment before save: doctor={appointment.doctor}, nurse={appointment.nurse}")
                appointment.save()
                logger.info(f"Appointment after save: doctor={appointment.doctor}, nurse={appointment.nurse}")
                messages.success(request, 'Appointment booked successfully.')
                return redirect('view_appointments')
            except ValidationError as e:
                logger.error(f"Validation error when booking appointment: {str(e)}")
                form.add_error(None, str(e))
            except Exception as e:
                logger.error(f"Unexpected error when booking appointment: {str(e)}")
                messages.error(request, f"Error booking appointment: {str(e)}")
        else:
            logger.error(f"Form invalid: {form.errors}")
    else:
        form = AppointmentForm()
    
    return render(request, 'appointments/book_appointment.html', {
        'form': form,
        'GOOGLE_MAPS_API_KEY': settings.GOOGLE_MAPS_API_KEY
    })
    
def load_staff(request):
    doctor_or_nurse = request.GET.get('doctor_or_nurse')
    if doctor_or_nurse == 'doctor':
        staff = User.objects.filter(user_type='doctor')
    else:
        staff = User.objects.filter(user_type='nurse')
    
    staff_list = [{'id': member.id, 'name': member.get_full_name()} for member in staff]
    return JsonResponse(staff_list, safe=False)

@login_required
def get_available_slots(request):
    date = request.GET.get('date')
    staff_id = request.GET.get('staff_id')
    doctor_or_nurse = request.GET.get('doctor_or_nurse')

    available_slots = ["08:00", "08:10", "08:20", "08:30", "08:40", "08:50", "09:00", "09:10"]

    booked_appointments = Appointment.objects.filter(date=date, **{doctor_or_nurse: staff_id}).values_list('time', flat=True)
    available_slots = [slot for slot in available_slots if slot not in booked_appointments]

    return JsonResponse(available_slots, safe=False)

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.staff = form.cleaned_data['staff']
            if form.cleaned_data['doctor_or_nurse'] == 'doctor':
                appointment.doctor = form.cleaned_data['staff']
                appointment.nurse = None
            else:
                appointment.nurse = form.cleaned_data['staff']
                appointment.doctor = None
            appointment.save()
            try:
                appointment.sync_with_google_calendar()
            except RefreshError:
                flow = create_flow(request)
                authorization_url, _ = flow.authorization_url(prompt='consent')
                return redirect(authorization_url)
            except Exception as e:
                messages.error(request, f"Error syncing with Google Calendar: {str(e)}")
            messages.success(request, 'Appointment rescheduled successfully.')
            return redirect('view_appointments')
    else:
        form = AppointmentForm(instance=appointment, initial={'doctor_or_nurse': 'doctor' if appointment.doctor else 'nurse'})
    return render(request, 'appointments/reschedule_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def view_appointments(request):
    if request.user.is_patient():
        appointments = Appointment.objects.filter(patient=request.user)
    elif request.user.is_doctor():
        appointments = Appointment.objects.filter(doctor=request.user)
    elif request.user.is_nurse():
        appointments = Appointment.objects.filter(nurse=request.user)
    else:
        appointments = Appointment.objects.all()
    return render(request, 'appointments/view_appointments.html', {'appointments': appointments})

@login_required
@user_is_doctor
def issue_prescription(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.patient = appointment.patient
            prescription.doctor = request.user
            prescription.appointment = appointment
            prescription.save()
            return redirect('doctor_dashboard')
    else:
        form = PrescriptionForm()
    return render(request, 'appointments/issue_prescription.html', {'form': form, 'appointment': appointment})

@login_required
def view_prescriptions(request):
    if request.user.is_patient():
        prescriptions = Prescription.objects.filter(patient=request.user)
    elif request.user.is_doctor():
        prescriptions = Prescription.objects.filter(doctor=request.user)
    else:
        prescriptions = Prescription.objects.none()
    return render(request, 'appointments/view_prescriptions.html', {'prescriptions': prescriptions})

@login_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if request.user != prescription.patient and request.user != prescription.doctor:
        return redirect('unauthorized_access')
    return render(request, 'appointments/prescription_detail.html', {'prescription': prescription})

@login_required
def appointment_detail(request, appointment_id):
    if request.user.is_patient():
        appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    elif request.user.is_doctor():
        appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    elif request.user.is_nurse():
        appointment = get_object_or_404(Appointment, id=appointment_id, nurse=request.user)
    else:
        appointment = get_object_or_404(Appointment, id=appointment_id)
    prescriptions = appointment.prescriptions.all()
    return render(request, 'appointments/appointment_detail.html', {'appointment': appointment, 'prescriptions': prescriptions})

@login_required
@user_is_patient
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, patient=request.user)
    if request.method == 'POST':
        try:
            appointment.delete()
            messages.success(request, 'Appointment cancelled successfully.')
        except Exception as e:
            messages.error(request, f"Error cancelling appointment: {str(e)}")
        return redirect('view_appointments')
    return render(request, 'appointments/cancel_appointment.html', {'appointment': appointment})

@login_required
@user_is_doctor
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    if request.method == 'POST':
        appointment.is_completed = True
        appointment.save()
        invoice = Invoice(
            patient=appointment.patient,
            appointment=appointment,
            patient_type='NHS' if appointment.patient.is_nhs_patient else 'PRIVATE',
            consultation_length=(appointment.end_time - appointment.start_time).minutes,
            rate=Decimal('50.00')
        )
        invoice.save()
        messages.success(request, 'Appointment marked as completed and invoice generated.')
        return redirect('view_invoice', invoice_id=invoice.id)
    return render(request, 'appointments/complete_appointment.html', {'appointment': appointment})

def oauth2callback(request):
    flow = create_flow(request)
    flow.fetch_token(code=request.GET.get('code'))
    credentials = flow.credentials
    request.session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    return redirect('book_appointment')

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

@login_required
@user_is_doctor
def generate_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save(commit=False)
            invoice.patient = appointment.patient
            invoice.appointment = appointment
            invoice.save()
            return redirect('view_invoice', invoice_id=invoice.id)
    else:
        form = InvoiceForm(initial={'appointment': appointment})
    return render(request, 'appointments/generate_invoice.html', {'form': form, 'appointment': appointment})

@login_required
def view_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.user != invoice.patient and not request.user.is_doctor() and not request.user.is_admin():
        return redirect('unauthorized_access')
    return render(request, 'appointments/view_invoice.html', {'invoice': invoice})

@login_required
@user_is_patient
def patient_invoices(request):
    invoices = Invoice.objects.filter(patient=request.user)
    return render(request, 'appointments/patient_invoices.html', {'invoices': invoices})

@login_required
@user_is_admin
def admin_invoices(request):
    invoices = Invoice.objects.all()
    nhs_charges = sum(invoice.total_amount for invoice in invoices if invoice.patient_type == 'NHS')
    private_payments = sum(invoice.total_amount for invoice in invoices if invoice.patient_type == 'PRIVATE' and invoice.payment_status == 'PAID')
    total_turnover = sum(invoice.total_amount for invoice in invoices)
    context = {
        'invoices': invoices,
        'nhs_charges': nhs_charges,
        'private_payments': private_payments,
        'total_turnover': total_turnover,
    }
    return render(request, 'appointments/admin_invoices.html', context)

@login_required
@user_is_admin
def financial_reports(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
    invoices = Invoice.objects.filter(date_issued__range=[start_date, end_date])
    daily_turnover = invoices.values('date_issued__date').annotate(total=Sum('total_amount'))
    weekly_turnover = invoices.values('date_issued__week').annotate(total=Sum('total_amount'))
    monthly_turnover = invoices.values('date_issued__month').annotate(total=Sum('total_amount'))
    nhs_charges = invoices.filter(patient_type='NHS').aggregate(total=Sum('total_amount'))['total'] or 0
    private_payments = invoices.filter(patient_type='PRIVATE', payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    total_turnover = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
    context = {
        'daily_turnover': daily_turnover,
        'weekly_turnover': weekly_turnover,
        'monthly_turnover': monthly_turnover,
        'nhs_charges': nhs_charges,
        'private_payments': private_payments,
        'total_turnover': total_turnover,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'appointments/financial_reports.html', context)

@login_required
@user_is_admin
def update_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        if form.is_valid():
            form.save()
            return redirect('view_invoice', invoice_id=invoice.id)
    else:
        form = InvoiceForm(instance=invoice)
    return render(request, 'appointments/update_invoice.html', {'form': form, 'invoice': invoice})

@login_required
@user_is_doctor
@user_is_nurse
@user_is_admin
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
