
from django import forms
from .models import Appointment, Prescription  # Ensure both models are imported
from authentication.models import User
from django.utils import timezone

class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'dosage', 'instructions', 'is_repeatable']

class AppointmentForm(forms.ModelForm):
    doctor_or_nurse = forms.ChoiceField(choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')])
    staff = forms.ModelChoiceField(queryset=User.objects.filter(user_type__in=['doctor', 'nurse']), required=False)

    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason', 'address']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs:
            doctor_or_nurse = kwargs['initial'].get('doctor_or_nurse')
        else:
            doctor_or_nurse = self.data.get('doctor_or_nurse')
        if doctor_or_nurse:
            self.fields['staff'].queryset = User.objects.filter(user_type=doctor_or_nurse)
        else:
            self.fields['staff'].queryset = User.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        doctor_or_nurse = cleaned_data.get('doctor_or_nurse')
        staff = cleaned_data.get('staff')

        if date and date < timezone.now().date():
            raise forms.ValidationError("Appointment date cannot be in the past")

        if date and time and staff:
            existing_appointment = Appointment.objects.filter(
                date=date,
                time=time,
                **{doctor_or_nurse: staff}
            ).exists()
            if existing_appointment:
                raise forms.ValidationError("This time slot is already booked")

        if doctor_or_nurse == 'doctor':
            cleaned_data['doctor'] = staff
            cleaned_data['nurse'] = None
        else:
            cleaned_data['nurse'] = staff
            cleaned_data['doctor'] = None

        return cleaned_data
