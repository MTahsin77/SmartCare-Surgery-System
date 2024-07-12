from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from authentication.models import User, GPDetails
from appointments.models import Prescription
from .decorators import user_is_medical_staff
from .models import SharedPatientRecord
import json

@login_required
@user_is_medical_staff
def share_patient_record(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        patient_id = data.get('patient_id')
        gp_id = data.get('gp_id')
        message = data.get('message')

        try:
            patient = User.objects.get(id=patient_id)
            gp = GPDetails.objects.get(id=gp_id)

            SharedPatientRecord.objects.create(
                patient=patient,
                gp=gp,
                shared_by=request.user,
                message=message
            )

            patient_details = {
                'name': patient.get_full_name(),
                'email': patient.email,
                'date_of_birth': str(patient.date_of_birth),
                'address': patient.address,
                'phone_number': patient.phone_number,
                'patient_type': patient.get_patient_type_display(),
            }

            prescriptions = Prescription.objects.filter(patient=patient)
            prescription_details = [
                {
                    'medication': p.medication,
                    'dosage': p.dosage,
                    'instructions': p.instructions,
                    'date_prescribed': str(p.date_prescribed)
                } for p in prescriptions
            ]

            email_content = render_to_string('collaboration/share_patient_record_email.html', {
                'gp': gp,
                'patient': patient,
                'patient_details': patient_details,
                'prescriptions': prescription_details,
                'message': message
            })

            send_mail(
                'Patient Details Shared',
                email_content,
                settings.DEFAULT_FROM_EMAIL,
                [gp.email],
                fail_silently=False,
                html_message=email_content
            )

            return JsonResponse({'status': 'success'})
        except (User.DoesNotExist, GPDetails.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    patients = User.objects.filter(user_type='patient')

    if search_query:
        patients = patients.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(date_of_birth__icontains=search_query)
        )

    paginator = Paginator(patients, 10)
    page_obj = paginator.get_page(page_number)

    gps = GPDetails.objects.all()

    context = {
        'page_obj': page_obj,
        'gps': gps,
        'search_query': search_query,
    }

    return render(request, 'collaboration/share_patient_record.html', context)

@login_required
@user_is_medical_staff
def shared_records_list(request):
    shared_records = SharedPatientRecord.objects.all().order_by('-shared_date')
    return render(request, 'collaboration/shared_records_list.html', {'shared_records': shared_records})