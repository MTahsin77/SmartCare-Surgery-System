from django import forms
from .models import Appointment, Prescription, Invoice, PrescriptionRequest, Fee, Rate
from authentication.models import User
from django.utils import timezone
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AppointmentForm(forms.ModelForm):
    doctor_or_nurse = forms.ChoiceField(choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], required=True)
    specialty = forms.ChoiceField(choices=[('', 'Any Specialty')] + list(User.DOCTOR_SPECIALTIES), required=False)
    staff = forms.ModelChoiceField(queryset=User.objects.none(), required=True)

    class Meta:
        model = Appointment
        fields = ['date', 'time', 'reason', 'doctor_or_nurse', 'specialty', 'staff', 'appointment_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['specialty'].required = False
        if 'doctor_or_nurse' in self.data:
            if self.data.get('doctor_or_nurse') == 'doctor':
                self.fields['staff'].queryset = User.objects.filter(user_type='doctor')
            else:
                self.fields['staff'].queryset = User.objects.filter(user_type='nurse')
        elif self.instance.pk:
            if self.instance.doctor:
                self.fields['doctor_or_nurse'].initial = 'doctor'
                self.fields['staff'].queryset = User.objects.filter(user_type='doctor')
                self.fields['staff'].initial = self.instance.doctor
            elif self.instance.nurse:
                self.fields['doctor_or_nurse'].initial = 'nurse'
                self.fields['staff'].queryset = User.objects.filter(user_type='nurse')
                self.fields['staff'].initial = self.instance.nurse
            else:
                self.fields['staff'].queryset = User.objects.filter(user_type__in=['doctor', 'nurse'])

    def clean(self):
        cleaned_data = super().clean()
        doctor_or_nurse = cleaned_data.get('doctor_or_nurse')
        staff = cleaned_data.get('staff')

        if doctor_or_nurse == 'doctor':
            cleaned_data['doctor'] = staff
            cleaned_data['nurse'] = None
        elif doctor_or_nurse == 'nurse':
            cleaned_data['nurse'] = staff
            cleaned_data['doctor'] = None

        return cleaned_data


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'dosage', 'instructions', 'is_repeatable']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class PrescriptionRequestForm(forms.ModelForm):
    class Meta:
        model = PrescriptionRequest
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['patient_type', 'consultation_length', 'rate', 'payment_status']
        widgets = {
            'consultation_length': forms.NumberInput(attrs={'min': 10, 'step': 10}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = kwargs.pop('user', None)
        if not user or not user.is_admin():
            for field in self.fields:
                self.fields[field].widget.attrs['readonly'] = True

    def clean_consultation_length(self):
        length = self.cleaned_data.get('consultation_length')
        if length is not None and length % 10 != 0:
            raise forms.ValidationError("Consultation length must be in multiples of 10 minutes.")
        return length

class InvoiceStatusForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['payment_status']

class FeeForm(forms.ModelForm):
    class Meta:
        model = Fee
        fields = ['title', 'amount', 'patient_type']

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ['rate_type', 'amount']


class AppointmentTypeFilterForm(forms.Form):
    appointment_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Appointment.APPOINTMENT_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class DateRangeFilterForm(forms.Form):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

class RateSettingForm(forms.Form):
    nhs_rate = forms.DecimalField(max_digits=6, decimal_places=2, min_value=0)
    private_rate = forms.DecimalField(max_digits=6, decimal_places=2, min_value=0)

    def clean(self):
        cleaned_data = super().clean()
        nhs_rate = cleaned_data.get('nhs_rate')
        private_rate = cleaned_data.get('private_rate')

        if nhs_rate and nhs_rate <= 0:
            self.add_error('nhs_rate', "NHS rate must be greater than zero.")
        if private_rate and private_rate <= 0:
            self.add_error('private_rate', "Private rate must be greater than zero.")

        return cleaned_data

class DoctorSpecialtyFilterForm(forms.Form):
    specialty = forms.ChoiceField(choices=[('', 'All Specialties')] + list(User.DOCTOR_SPECIALTIES), required=False)
