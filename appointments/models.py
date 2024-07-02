# models.py
from django.db import models
from authentication.models import User
from django.conf import settings

class Appointment(models.Model):
    is_completed = models.BooleanField(default=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_doctor', null=True, blank=True)
    nurse = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_nurse', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True)
    doctor_or_nurse = models.CharField(max_length=10, choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], null=True, blank=True)

    def __str__(self):
        return f'Appointment with {self.doctor} on {self.date} at {self.time}'

class Prescription(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescribed')
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_repeatable = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medication} for {self.patient.username}"
