# dashboards/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication.decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin
from authentication.models import User, UserProfile
from appointments.models import Appointment
from .forms import UserForm, UserProfileForm, AppointmentForm, PrescriptionForm

@login_required
@user_is_patient
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'dashboards/patient_dashboard.html', {'appointments': appointments})

@login_required
@user_is_doctor
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    return render(request, 'dashboards/doctor_dashboard.html', {'appointments': appointments})

@login_required
@user_is_nurse
def nurse_dashboard(request):
    appointments = Appointment.objects.filter(nurse=request.user)
    return render(request, 'dashboards/nurse_dashboard.html', {'appointments': appointments})

@login_required
@user_is_admin
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@login_required
@user_is_admin
def manage_users(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            messages.success(request, 'User has been created/updated successfully.')
            return redirect('manage_users')
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    users = User.objects.all()
    return render(request, 'dashboards/manage_users.html', {'users': users, 'user_form': user_form, 'profile_form': profile_form})

@login_required
@user_is_admin
def manage_appointments(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if form.cleaned_data['doctor_or_nurse'] == 'doctor':
                appointment.doctor = form.cleaned_data['doctor']
                appointment.nurse = None
            else:
                appointment.nurse = form.cleaned_data['nurse']
                appointment.doctor = None
            appointment.save()
            messages.success(request, 'Appointment has been created/updated successfully.')
            return redirect('manage_appointments')
    else:
        form = AppointmentForm()
    
    appointments = Appointment.objects.all()
    return render(request, 'dashboards/manage_appointments.html', {'appointments': appointments, 'form': form})

@login_required
@user_is_admin
def approve_doctors(request):
    if request.method == 'POST':
        doctor_id = request.POST.get('doctor_id')
        doctor = User.objects.get(id=doctor_id)
        doctor.is_approved = True
        doctor.save()
        messages.success(request, f'Doctor {doctor.username} has been approved.')
        return redirect('approve_doctors')
    
    pending_doctors = User.objects.filter(user_type='doctor', is_approved=False)
    return render(request, 'dashboards/approve_doctors.html', {'pending_doctors': pending_doctors})

@login_required
@user_is_doctor
def issue_prescription(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    if request.method == 'POST':
        form = PrescriptionForm(request.POST)
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.appointment = appointment
            prescription.doctor = request.user
            prescription.save()
            messages.success(request, 'Prescription has been issued successfully.')
            return redirect('doctor_dashboard')
    else:
        form = PrescriptionForm()
    return render(request, 'dashboards/issue_prescription.html', {'form': form, 'appointment': appointment})

@login_required
@user_is_admin
def view_turnover(request):
    # This is a placeholder for the turnover view
    # You'll need to implement the logic to calculate and display turnover
    return render(request, 'dashboards/view_turnover.html')