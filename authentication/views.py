from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from appointments.models import Appointment
from .forms import AppointmentForm
from .models import UserProfile
from .decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            if user.is_patient():
                return redirect('patient_dashboard')
            elif user.is_doctor():
                return redirect('doctor_dashboard')
            elif user.is_nurse():
                return redirect('nurse_dashboard')
            else:
                return redirect('admin_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_admin():
                return redirect('admin_dashboard')
            elif user.is_doctor():
                return redirect('doctor_dashboard')
            elif user.is_nurse():
                return redirect('nurse_dashboard')
            else:
                return redirect('patient_dashboard')
    else:
        form = UserLoginForm()
    return render(request, 'authentication/login.html', {'form': form})

@login_required
@user_is_patient
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'authentication/patient_dashboard.html', {'appointments': appointments})

@login_required
@user_is_doctor
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    return render(request, 'authentication/doctor_dashboard.html', {'appointments': appointments})

@login_required
@user_is_nurse
def nurse_dashboard(request):
    appointments = Appointment.objects.filter(nurse=request.user)
    return render(request, 'authentication/nurse_dashboard.html', {'appointments': appointments})

@login_required
@user_is_admin
def admin_dashboard(request):
    all_appointments = Appointment.objects.all()
    return render(request, 'authentication/admin_dashboard.html', {'appointments': all_appointments})

@login_required
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'authentication/profile.html', {'form': form})

@login_required
def list_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments/list_appointments.html', {'appointments': appointments})

@login_required
def book_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = request.user
            appointment.save()
            return redirect('list_appointments')
        else:
            print(f"Form errors: {form.errors}") 
    else:
        form = AppointmentForm()
    return render(request, 'appointments/book_appointment.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def unauthorized_access(request):
    return render(request, 'authentication/unauthorized_access.html')