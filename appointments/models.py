from django.db import models
from authentication.models import User

class Appointment(models.Model):
    is_completed = models.BooleanField(default=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_doctor', null=True, blank=True)
    nurse = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments_as_nurse', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField()
    address = models.CharField(max_length=255, blank=True, null=True)  # Add this line if 'address' is required
    doctor_or_nurse = models.CharField(max_length=10, choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], null=True, blank=True)  # Add this line if 'doctor_or_nurse' is required

    def __str__(self):
        return f'Appointment with {self.doctor} on {self.date} at {self.time}'

class Prescription(models.Model):
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()

    def __str__(self):
        return f'Prescription for {self.appointment.patient} by {self.doctor}'
