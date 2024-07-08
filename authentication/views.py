from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, GPForm
from .models import UserProfile, GPDetails, PendingRegistration
from .decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            
            if user_type in ['doctor', 'nurse', 'admin']:
                user.is_active = False
                user.save()
                PendingRegistration.objects.create(user=user)
                messages.info(request, 'Your registration is pending admin approval. You will be notified once approved.')
                return redirect('login')
            else:
                user.save()
                login(request, user)
                messages.success(request, f'Account created for {user.username}. You are now logged in.')
                return redirect('patient_dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentication/register.html', {'form': form})

@login_required
@user_is_admin
def approve_registration(request, pending_id):
    pending = get_object_or_404(PendingRegistration, id=pending_id)
    user = pending.user
    user.is_active = True
    user.save()
    pending.delete()
    messages.success(request, f'Registration approved for {user.username}.')
    return redirect('pending_registrations')

@login_required
@user_is_admin
def pending_registrations(request):
    pending = PendingRegistration.objects.all()
    return render(request, 'authentication/pending_registrations.html', {'pending': pending})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
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
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user.userprofile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user.userprofile)
    return render(request, 'authentication/profile.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('login')

def unauthorized_access(request):
    return render(request, 'authentication/unauthorized_access.html')

@login_required
@user_is_patient
def patient_dashboard(request):
    return render(request, 'dashboards/patient_dashboard.html')

@login_required
@user_is_doctor
def doctor_dashboard(request):
    return render(request, 'dashboards/doctor_dashboard.html')

@login_required
@user_is_nurse
def nurse_dashboard(request):
    return render(request, 'dashboards/nurse_dashboard.html')

@login_required
@user_is_admin
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')

@login_required
@user_is_admin
def manage_gp(request, gp_id=None):
    if gp_id:
        gp = get_object_or_404(GPDetails, id=gp_id)
    else:
        gp = None

    if request.method == 'POST':
        form = GPForm(request.POST, instance=gp)
        if form.is_valid():
            form.save()
            messages.success(request, 'GP details saved successfully.')
            return redirect('gp_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = GPForm(instance=gp)

    return render(request, 'authentication/manage_gp.html', {'form': form, 'gp': gp})
    
@login_required
def delete_gp(request, gp_id):
    gp = get_object_or_404(GPDetails, id=gp_id)
    if request.method == 'POST':
        gp.delete()
        messages.success(request, 'GP deleted successfully.')
        return redirect('gp_list')
    return render(request, 'authentication/delete_gp.html', {'gp': gp})

@login_required
@user_is_admin
def gp_list(request):
    gps = GPDetails.objects.all()
    return render(request, 'authentication/gp_list.html', {'gps': gps})