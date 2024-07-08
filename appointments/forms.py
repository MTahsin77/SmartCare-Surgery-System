from django import forms
from .models import Appointment, Prescription, Invoice
from authentication.models import User
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ['medication', 'dosage', 'instructions', 'is_repeatable']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 4, 'cols': 40}),
        }

class AppointmentForm(forms.ModelForm):
    address = forms.CharField(widget=forms.TextInput(attrs={'id': 'address-input'}))
    latitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    longitude = forms.FloatField(widget=forms.HiddenInput(), required=False)
    doctor = forms.ModelChoiceField(queryset=User.objects.filter(user_type='doctor'), required=False)
    nurse = forms.ModelChoiceField(queryset=User.objects.filter(user_type='nurse'), required=False)

    class Meta:
        model = Appointment
        fields = ['doctor', 'nurse', 'date', 'time', 'reason', 'address']

    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        time = cleaned_data.get('time')
        doctor = cleaned_data.get('doctor')
        nurse = cleaned_data.get('nurse')

        if not date:
            self.add_error('date', "Appointment date is required")

        if not time:
            self.add_error('time', "Appointment time is required")

        if not cleaned_data.get('address'):
            self.add_error('address', "Appointment address is required")

        if not doctor and not nurse:
            self.add_error(None, "Appointment must be with either a doctor or a nurse, not both or neither.")

        if date and time and (doctor or nurse):
            existing_appointment = Appointment.objects.filter(
                date=date,
                time=time,
                doctor=doctor,
                nurse=nurse
            ).exists()
            if existing_appointment:
                self.add_error(None, "This time slot is already booked")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        logger.info(f"Saving appointment: doctor={self.cleaned_data.get('doctor')}, nurse={self.cleaned_data.get('nurse')}")
        
        if commit:
            instance.save()
        
        logger.info(f"Instance after save: doctor={instance.doctor}, nurse={instance.nurse}")
        return instance

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['consultation_length', 'rate', 'patient_type']
        widgets = {
            'consultation_length': forms.NumberInput(attrs={'min': 10, 'step': 10}),
        }

    def clean_consultation_length(self):
        length = self.cleaned_data.get('consultation_length')
        if length is not None and length % 10 != 0:
            raise forms.ValidationError("Consultation length must be in multiples of 10 minutes.")
        return length

    def clean_rate(self):
        rate = self.cleaned_data.get('rate')
        if rate is not None and rate <= 0:
            raise forms.ValidationError("Rate must be greater than zero.")
        return rate
