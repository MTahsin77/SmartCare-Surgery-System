from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import connection, transaction
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from .models import Rate, DefaultRate
from .forms import InvoiceStatusForm, RateForm
from smartcare import settings
from .calendar_service import create_flow, get_calendar_service
from .forms import (AppointmentForm, PrescriptionForm, InvoiceForm, PrescriptionRequestForm,
                    FeeForm, DoctorSpecialtyFilterForm, AppointmentTypeFilterForm, DateRangeFilterForm,
                    RateSettingForm)
from .models import (Appointment, Prescription, Invoice, CompletedForwardedCanceled,
                     PrescriptionRequest, Fee, User)
from authentication.decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin
from django.utils import timezone
from google.auth.exceptions import RefreshError
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, timedelta
import logging
from .forms import DoctorSpecialtyFilterForm

logger = logging.getLogger(__name__)

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            doctor_or_nurse = form.cleaned_data['doctor_or_nurse']
            staff = form.cleaned_data['staff']
            if doctor_or_nurse == 'doctor':
                appointment.doctor = staff
                appointment.nurse = None
            else:
                appointment.nurse = staff
                appointment.doctor = None
            appointment.save()
            messages.success(request, 'Appointment booked successfully.')
            return redirect('view_appointments')
        else:
            messages.error(request, 'There was an error booking your appointment. Please check the form.')
    else:
        form = AppointmentForm()
    
    context = {
        'form': form,
    }
    return render(request, 'appointments/book_appointment.html', context)

@login_required
def reschedule_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            updated_appointment = form.save(commit=False)
            doctor_or_nurse = form.cleaned_data['doctor_or_nurse']
            staff = form.cleaned_data['staff']
            if doctor_or_nurse == 'doctor':
                updated_appointment.doctor = staff
                updated_appointment.nurse = None
            else:
                updated_appointment.nurse = staff
                updated_appointment.doctor = None
            updated_appointment.save()
            messages.success(request, 'Appointment rescheduled/forwarded successfully.')
            return redirect('view_appointments')
        else:
            messages.error(request, 'There was an error rescheduling/forwarding your appointment. Please check the form.')
    else:
        initial_data = {
            'doctor_or_nurse': 'doctor' if appointment.doctor else 'nurse',
            'staff': appointment.doctor.id if appointment.doctor else appointment.nurse.id,
            'specialty': appointment.doctor.specialty if appointment.doctor else None,
        }
        form = AppointmentForm(instance=appointment, initial=initial_data)
    
    context = {
        'form': form,
        'appointment': appointment,
    }
    return render(request, 'appointments/reschedule_appointment.html', context)


@login_required
def cancel_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'SCHEDULED':
        messages.error(request, "This appointment cannot be cancelled as it's not in a scheduled state.")
        return redirect('view_appointments')

    if not (request.user == appointment.patient or 
            request.user == appointment.doctor or 
            request.user == appointment.nurse or 
            request.user.is_staff):
        messages.error(request, "You don't have permission to cancel this appointment.")
        return redirect('view_appointments')

    if request.method == 'POST':
        cancellation_reason = request.POST.get('cancellation_reason', '')
        appointment.update_status('CANCELED')
        CompletedForwardedCanceled.objects.create(
            appointment=appointment,
            changed_by=request.user,
            reason=cancellation_reason
        )
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('view_appointments')
    
    return render(request, 'appointments/cancel_appointment.html', {'appointment': appointment})


@login_required
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        if appointment.status != 'SCHEDULED':
            messages.error(request, "This appointment cannot be completed as it's not in a scheduled state.")
            return redirect('view_appointments')
        
        appointment.update_status('COMPLETED')
        
        CompletedForwardedCanceled.objects.create(
            appointment=appointment,
            changed_by=request.user,
            reason="Appointment completed"
        )
        
        return redirect('generate_invoice', appointment_id=appointment.id)
    return render(request, 'appointments/complete_appointment.html', {'appointment': appointment})


@login_required
def view_appointments(request):
    filter_form = AppointmentTypeFilterForm(request.GET)
    appointments = Appointment.objects.filter(status='SCHEDULED')

    if request.user.is_patient():
        appointments = appointments.filter(patient=request.user)
    elif request.user.is_doctor():
        appointments = appointments.filter(doctor=request.user)
    elif request.user.is_nurse():
        appointments = appointments.filter(nurse=request.user)

    if filter_form.is_valid() and filter_form.cleaned_data['appointment_type']:
        appointments = appointments.filter(appointment_type=filter_form.cleaned_data['appointment_type'])

    context = {
        'appointments': appointments,
        'filter_form': filter_form
    }
    return render(request, 'appointments/view_appointments.html', context)

@login_required
def view_cfc_appointments(request):
    cfc_appointments = Appointment.objects.exclude(status='SCHEDULED')
    
    if request.user.is_patient():
        cfc_appointments = cfc_appointments.filter(patient=request.user)
    elif request.user.is_doctor():
        cfc_appointments = cfc_appointments.filter(doctor=request.user)
    elif request.user.is_nurse():
        cfc_appointments = cfc_appointments.filter(nurse=request.user)
    
    cfc_appointments = cfc_appointments.order_by('-date', '-time')
    return render(request, 'appointments/cfc.html', {'cfc_appointments': cfc_appointments})

@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.user.is_patient():
        if appointment.patient != request.user:
            raise PermissionDenied
    elif request.user.is_doctor():
        if appointment.doctor != request.user:
            raise PermissionDenied
    elif request.user.is_nurse():
        if appointment.nurse != request.user:
            raise PermissionDenied
    elif not request.user.is_admin():
        raise PermissionDenied
    
    prescriptions = appointment.prescriptions.all()
    
    context = {
        'appointment': appointment,
        'prescriptions': prescriptions,
        'doctor': appointment.doctor,
        'nurse': appointment.nurse,
        'patient': appointment.patient,
        'raw_status': appointment.status,
    }
    
    return render(request, 'appointments/appointment_detail.html', context)


@login_required
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
            return redirect('appointment_detail', appointment_id=appointment.id)
    else:
        form = PrescriptionForm()
    return render(request, 'appointments/issue_prescription.html', {'form': form, 'appointment': appointment})

@login_required
def view_prescriptions(request):
    if request.user.is_patient():
        prescriptions = Prescription.objects.filter(patient=request.user)
        return render(request, 'appointments/view_prescriptions.html', {'prescriptions': prescriptions})

    elif request.user.is_doctor() or request.user.is_nurse():
        if request.method == 'POST':
            request_id = request.POST.get('request_id')
            if request_id:
                prescription_request = get_object_or_404(PrescriptionRequest, id=request_id)
                status = request.POST.get('status')
                prescription_request.status = status
                prescription_request.save()
                
                if status == 'APPROVED':
                    prescription = prescription_request.prescription
                    prescription.date_prescribed = timezone.now()
                    prescription.is_repeatable = True  
                    prescription.save()
                    
                    PrescriptionRequest.objects.filter(id=request_id).delete()
                    
                messages.success(request, f'Prescription request {status.lower()}.')
                return redirect('view_prescriptions')

        prescription_requests = PrescriptionRequest.objects.filter(prescription__doctor=request.user)
        return render(request, 'appointments/view_prescriptions.html', {'prescription_requests': prescription_requests})
    else:
        return redirect('home')


@login_required
def prescription_detail(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id)
    if request.user != prescription.patient and request.user != prescription.doctor:
        return redirect('unauthorized_access')
    return render(request, 'appointments/prescription_detail.html', {'prescription': prescription})

@login_required
@user_is_patient
def request_prescription(request, prescription_id):
    prescription = get_object_or_404(Prescription, id=prescription_id, patient=request.user)
    if request.method == 'POST':
        form = PrescriptionRequestForm(request.POST)
        if form.is_valid():
            prescription_request = form.save(commit=False)
            prescription_request.patient = request.user
            prescription_request.prescription = prescription
            prescription_request.save()
            messages.success(request, 'Prescription request submitted successfully.')
            return redirect('view_prescriptions')
    else:
        form = PrescriptionRequestForm()
    return render(request, 'appointments/request_prescription.html', {'form': form, 'prescription': prescription})


from datetime import datetime

@login_required
def generate_invoice(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if request.method == 'POST':
        patient_type = appointment.patient.patient_type if hasattr(appointment.patient, 'patient_type') else 'NHS'
        
        invoice = Invoice(
            patient=appointment.patient,
            appointment=appointment,
            patient_type=patient_type,
            consultation_length=(appointment.end_time.hour * 60 + appointment.end_time.minute) - (appointment.time.hour * 60 + appointment.time.minute)
        )
        
        if appointment.doctor:
            invoice.rate = get_default_doctor_rate()
        elif appointment.nurse:
            invoice.rate = get_default_nurse_rate()
        else:
            invoice.rate = get_default_rate_for_patient_type(patient_type)
        
        invoice.save()

        applicable_fees = Fee.objects.filter(patient_type__in=['ALL', patient_type])
        invoice.fees.set(applicable_fees)
        
        invoice.total_amount = invoice.calculate_total()
        invoice.save()
        
        appointment.update_status('COMPLETED')
        
        CompletedForwardedCanceled.objects.create(
            appointment=appointment,
            changed_by=request.user,
            reason="Invoice generated and appointment completed"
        )
        
        messages.success(request, 'Invoice generated successfully and appointment marked as completed.')
        if request.user.is_admin():
            return redirect('list_invoices')
        elif request.user.is_doctor() or request.user.is_nurse():
            return redirect('view_edit_invoice', invoice_id=invoice.id)
    
    context = {
        'appointment': appointment,
    }
    return render(request, 'appointments/generate_invoice.html', context)


@login_required
def view_edit_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    if request.user.is_patient():
        if invoice.patient != request.user:
            raise PermissionDenied
    elif request.user.is_doctor():
        if invoice.appointment.doctor != request.user:
            raise PermissionDenied
    elif request.user.is_nurse():
        if invoice.appointment.nurse != request.user:
            raise PermissionDenied
    elif not request.user.is_admin():
        raise PermissionDenied
    
    can_edit = request.user.is_admin() or request.user.is_doctor() or request.user.is_nurse()
    
    if request.method == 'POST' and can_edit:
        if request.user.is_admin():
            form = InvoiceForm(request.POST, instance=invoice)
        else:
            form = InvoiceStatusForm(request.POST, instance=invoice)
        
        if form.is_valid():
            updated_invoice = form.save(commit=False)
            if updated_invoice.payment_status == 'PAID' and invoice.payment_status != 'PAID':
                updated_invoice.date_paid = timezone.now()

            updated_invoice.total_amount = updated_invoice.calculate_total()
            
            updated_invoice.save()
            messages.success(request, 'Invoice updated successfully.')
            return redirect('view_edit_invoice', invoice_id=invoice.id)
    else:
        if request.user.is_admin():
            form = InvoiceForm(instance=invoice)
        else:
            form = InvoiceStatusForm(instance=invoice)
    
    context = {
        'invoice': invoice,
        'form': form,
        'can_edit': can_edit,
        'issued_by': invoice.appointment.doctor.get_full_name() if invoice.appointment.doctor else invoice.appointment.nurse.get_full_name(),
        'staff_name': invoice.appointment.doctor.get_full_name() if invoice.appointment.doctor else invoice.appointment.nurse.get_full_name(),
        'appointment_type': invoice.appointment.get_appointment_type_display(),
    }
    return render(request, 'appointments/view_edit_invoice.html', context)

@login_required
def list_invoices(request):
    if request.user.is_admin():
        invoices = Invoice.objects.all()
    elif request.user.is_doctor():
        invoices = Invoice.objects.filter(appointment__doctor=request.user)
    elif request.user.is_nurse():
        invoices = Invoice.objects.filter(appointment__nurse=request.user)
    else:
        invoices = Invoice.objects.none()
    
    return render(request, 'appointments/list_invoices.html', {'invoices': invoices})

@login_required
@user_is_patient
def patient_invoices(request):
    invoices = Invoice.objects.filter(patient=request.user)
    return render(request, 'appointments/patient_invoices.html', {'invoices': invoices})

@login_required
@user_is_admin
def admin_invoices(request):
    fee_form = FeeForm()
    rate_form = RateForm()
    date_range_form = DateRangeFilterForm()

    if request.method == 'POST':
        if 'fee_form' in request.POST:
            fee_form = FeeForm(request.POST)
            if fee_form.is_valid():
                fee_form.save()
                messages.success(request, 'Fee added successfully.')
                return redirect('admin_invoices')
        elif 'rate_form' in request.POST:
            rate_form = RateForm(request.POST)
            if rate_form.is_valid():
                rate_type = rate_form.cleaned_data['rate_type']
                amount = rate_form.cleaned_data['amount']
                Rate.objects.update_or_create(
                    rate_type=rate_type,
                    defaults={'amount': amount}
                )
                messages.success(request, f'{rate_type} rate updated successfully.')
                return redirect('admin_invoices')
        elif 'date_range_form' in request.POST:
            date_range_form = DateRangeFilterForm(request.POST)
            if date_range_form.is_valid():
                start_date = date_range_form.cleaned_data['start_date']
                end_date = date_range_form.cleaned_data['end_date']
                invoices = Invoice.objects.filter(date_issued__range=[start_date, end_date])
            else:
                invoices = Invoice.objects.all()
        else:
            invoices = Invoice.objects.all()
    else:
        fee_form = FeeForm()
        rate_form = RateForm()
        date_range_form = DateRangeFilterForm()
        invoices = Invoice.objects.all()

    start_date = date_range_form.cleaned_data.get('start_date') if date_range_form.is_valid() else timezone.now().date() - timedelta(days=30)
    end_date = date_range_form.cleaned_data.get('end_date') if date_range_form.is_valid() else timezone.now().date()

    invoices = Invoice.objects.filter(date_issued__range=[start_date, end_date])
    nhs_charges = invoices.filter(patient_type='NHS').aggregate(total=Sum('total_amount'))['total'] or 0
    private_payments = invoices.filter(patient_type='PRIVATE', payment_status='PAID').aggregate(total=Sum('total_amount'))['total'] or 0
    total_turnover = invoices.aggregate(total=Sum('total_amount'))['total'] or 0

    context = {
        'fee_form': fee_form,
        'rate_form': rate_form,
        'date_range_form': date_range_form,
        'fees': Fee.objects.all(),
        'rates': Rate.objects.all(),
        'invoices': invoices,
        'nhs_charges': nhs_charges,
        'private_payments': private_payments,
        'total_turnover': total_turnover,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'appointments/admin_invoices.html', context)

@login_required
@user_is_admin
def delete_fee(request, fee_id):
    fee = get_object_or_404(Fee, id=fee_id)
    fee.delete()
    messages.success(request, 'Fee deleted successfully.')
    return redirect('admin_invoices')

@login_required
@user_is_admin
def financial_reports(request):
    date_range_form = DateRangeFilterForm(request.GET)
    start_date = date_range_form.cleaned_data.get('start_date') if date_range_form.is_valid() else timezone.now().date() - timedelta(days=30)
    end_date = date_range_form.cleaned_data.get('end_date') if date_range_form.is_valid() else timezone.now().date()

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
        'date_range_form': date_range_form,
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'appointments/financial_reports.html', context)

@login_required
def load_staff(request):
    doctor_or_nurse = request.GET.get('doctor_or_nurse')
    specialty = request.GET.get('specialty')
    
    if doctor_or_nurse == 'doctor':
        staff = User.objects.filter(user_type='doctor')
        if specialty:
            staff = staff.filter(specialty=specialty)
    else:
        staff = User.objects.filter(user_type='nurse')
    
    staff_list = [{'id': s.id, 'name': s.get_full_name()} for s in staff]
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

def get_rate_for_patient_type(patient_type):
    try:
        if patient_type == 'NHS':
            return Rate.objects.get(rate_type='NHS_PATIENT').amount
        elif patient_type == 'PRIVATE':
            return Rate.objects.get(rate_type='PRIVATE_PATIENT').amount
        else:
            raise ValueError(f"Invalid patient type: {patient_type}")
    except ObjectDoesNotExist:
        raise ValueError(f"Rate not set for patient type: {patient_type}")

def get_doctor_rate():
    try:
        return Rate.objects.get(rate_type='DOCTOR').amount
    except ObjectDoesNotExist:
        raise ValueError("Doctor rate not set")

def get_nurse_rate():
    try:
        return Rate.objects.get(rate_type='NURSE').amount
    except ObjectDoesNotExist:
        raise ValueError("Nurse rate not set")
    
def get_default_doctor_rate():
    try:
        return DefaultRate.objects.get(rate_type='DOCTOR').amount
    except DefaultRate.DoesNotExist:
        return Decimal('20.00')

def get_default_nurse_rate():
    try:
        return DefaultRate.objects.get(rate_type='NURSE').amount
    except DefaultRate.DoesNotExist:
        return Decimal('10.00')

def get_default_rate_for_patient_type(patient_type):
    rate_type = 'NHS_PATIENT' if patient_type == 'NHS' else 'PRIVATE_PATIENT'
    try:
        return DefaultRate.objects.get(rate_type=rate_type).amount
    except DefaultRate.DoesNotExist:
        return Decimal('00.00') if patient_type == 'NHS' else Decimal('00.00')