# forms.py

from django import forms
from .models import Appointment
from authentication.models import User

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
        doctor_or_nurse = cleaned_data.get('doctor_or_nurse')
        staff = cleaned_data.get('staff')

        if doctor_or_nurse == 'doctor':
            cleaned_data['doctor'] = staff
            cleaned_data['nurse'] = None
        else:
            cleaned_data['nurse'] = staff
            cleaned_data['doctor'] = None

        return cleaned_data
