from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import AppointmentForm, PrescriptionForm
from .models import Appointment, Prescription
from authentication.decorators import user_is_patient, user_is_doctor, user_is_nurse
from authentication.models import User 

@login_required
@user_is_patient
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.staff = form.cleaned_data['staff']
            if form.cleaned_data['doctor_or_nurse'] == 'doctor':
                appointment.doctor = form.cleaned_data['staff']
                appointment.nurse = None
            else:
                appointment.nurse = form.cleaned_data['staff']
                appointment.doctor = None
            appointment.save()
            messages.success(request, 'Appointment booked successfully.')
            return redirect('view_appointments')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book_appointment.html', {'form': form})

@login_required
@user_is_doctor
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
        appointment.delete()
        messages.success(request, 'Appointment cancelled successfully.')
        return redirect('view_appointments')
    return render(request, 'appointments/cancel_appointment.html', {'appointment': appointment})

@login_required
@user_is_doctor
def complete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id, doctor=request.user)
    if request.method == 'POST':
        appointment.is_completed = True
        appointment.save()
        messages.success(request, 'Appointment marked as completed.')
        return redirect('view_appointments')
    return render(request, 'appointments/complete_appointment.html', {'appointment': appointment})

def load_staff(request):
    doctor_or_nurse = request.GET.get('doctor_or_nurse')
    staff = User.objects.filter(user_type=doctor_or_nurse)
    return render(request, 'appointments/staff_dropdown_list_options.html', {'staff': staff})

@login_required
def get_available_slots(request):
    date = request.GET.get('date')
    doctor_id = request.GET.get('doctor_id')
    available_slots = ["09:00", "10:00", "11:00", "14:00", "15:00", "16:00"]
    return JsonResponse(available_slots, safe=False)
