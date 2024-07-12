from django.db import models
from django.conf import settings
from authentication.models import GPDetails

class SharedPatientRecord(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_records')
    gp = models.ForeignKey(GPDetails, on_delete=models.CASCADE)
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_by_records')
    shared_date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Record of {self.patient} shared with {self.gp} by {self.shared_by} on {self.shared_date}"
