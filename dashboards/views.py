from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from authentication.decorators import user_is_patient, user_is_doctor, user_is_nurse, user_is_admin
from authentication.models import User
from appointments.models import Appointment, Invoice, Prescription
from .forms import CustomUserCreationForm, CustomUserChangeForm

@login_required
@user_is_patient
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)
    prescriptions = Prescription.objects.filter(patient=request.user)
    invoices = Invoice.objects.filter(patient=request.user)
    context = {
        'appointments': appointments,
        'prescriptions': prescriptions,
        'invoices': invoices,
    }
    return render(request, 'dashboards/patient_dashboard.html', context)

@login_required
@user_is_doctor
def doctor_dashboard(request):
    appointments = Appointment.objects.filter(doctor=request.user)
    prescriptions = Prescription.objects.filter(doctor=request.user)
    context = {
        'appointments': appointments,
        'prescriptions': prescriptions,
    }
    return render(request, 'dashboards/doctor_dashboard.html', context)

@login_required
@user_is_nurse
def nurse_dashboard(request):
    appointments = Appointment.objects.filter(nurse=request.user)
    context = {
        'appointments': appointments,
    }
    return render(request, 'dashboards/nurse_dashboard.html', context)

@login_required
@user_is_admin
def admin_dashboard(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

    invoices = Invoice.objects.filter(date_issued__range=[start_date, end_date])

    daily_turnover = invoices.values('date_issued__date').annotate(total=Sum('total_amount'))
    weekly_turnover = invoices.values('date_issued__week').annotate(total=Sum('total_amount'))
    monthly_turnover = invoices.values('date_issued__month').annotate(total=Sum('total_amount'))

    patient_stats = Appointment.objects.filter(date__range=[start_date, end_date]).values('patient__user_type').annotate(count=Count('id'))

    context = {
        'daily_turnover': daily_turnover,
        'weekly_turnover': weekly_turnover,
        'monthly_turnover': monthly_turnover,
        'patient_stats': patient_stats,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, 'dashboards/admin_dashboard.html', context)

@login_required
@user_is_admin
def manage_users(request):
    user_type_filter = request.GET.get('user_type')
    user_role_filter = request.GET.get('user_role')

    users = User.objects.all()

    if user_type_filter:
        users = users.filter(patient_type=user_type_filter)
    if user_role_filter:
        users = users.filter(user_type=user_role_filter)

    if request.method == 'POST':
        if 'edit_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            form = CustomUserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, 'User has been updated successfully.')
                return redirect('manage_users')
        elif 'delete_user' in request.POST:
            user_id = request.POST.get('user_id')
            user = get_object_or_404(User, id=user_id)
            user.delete()
            messages.success(request, 'User has been deleted successfully.')
            return redirect('manage_users')
    else:
        form = CustomUserChangeForm()

    context = {
        'users': users,
        'form': form,
        'user_type_filter': user_type_filter,
        'user_role_filter': user_role_filter,
    }
    return render(request, 'dashboards/manage_users.html', context)

@login_required
@user_is_admin
def manage_appointments(request):
    appointments = Appointment.objects.all().order_by('-date', '-time')
    context = {
        'appointments': appointments,
    }
    return render(request, 'dashboards/manage_appointments.html', context)
