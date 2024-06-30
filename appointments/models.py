from django.db import models
from authentication.models import User

class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_appointments')
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(null=True, blank=True)
    doctor_or_nurse = models.CharField(max_length=50)
    address = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Appointment with {self.doctor} on {self.date} at {self.time}"
