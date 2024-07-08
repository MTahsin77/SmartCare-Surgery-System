from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal

class Appointment(models.Model):
    STAFF_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse')
    ]
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='appointments_as_doctor', null=True, blank=True)
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='appointments_as_nurse', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField()
    reason = models.TextField(help_text="Reason for the appointment", blank=True, default="General checkup")
    address = models.CharField(max_length=255, blank=True, null=True, help_text="Address where the appointment will take place")
    is_completed = models.BooleanField(default=False)
    doctor_or_nurse = models.CharField(max_length=10, choices=STAFF_CHOICES, null=True, blank=True)

    def clean(self):
        super().clean()
        if self.date is not None and self.date < timezone.now().date():
            raise ValidationError("Appointment date cannot be in the past.")
        if bool(self.doctor) == bool(self.nurse):
            raise ValidationError("Appointment must be with either a doctor or a nurse, not both or neither.")
        if self.doctor_or_nurse == 'doctor' and not self.doctor:
            raise ValidationError("Doctor must be selected.")
        if self.doctor_or_nurse == 'nurse' and not self.nurse:
            raise ValidationError("Nurse must be selected.")
        if self.date and self.time and self.doctor_or_nurse:
            existing_appointment = Appointment.objects.filter(
                date=self.date,
                time=self.time,
                **{self.doctor_or_nurse: self.doctor or self.nurse}
            ).exclude(id=self.id).exists()
            if existing_appointment:
                raise ValidationError("This time slot is already booked.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Prescription(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescribed')
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='prescriptions')
    medication = models.CharField(max_length=100)
    dosage = models.CharField(max_length=100)
    instructions = models.TextField()
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_repeatable = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.medication} for {self.patient.username}"

class Invoice(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('NHS', 'NHS'),
        ('PRIVATE', 'Private'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('SENT_TO_NHS', 'Sent to NHS'),
    ]

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='invoices')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, unique=True)
    patient_type = models.CharField(max_length=7, choices=PATIENT_TYPE_CHOICES)
    consultation_length = models.PositiveIntegerField(help_text="Length of consultation in minutes")
    rate = models.DecimalField(max_digits=6, decimal_places=2, help_text="Rate per 10 minutes")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
    date_issued = models.DateTimeField(default=timezone.now)
    date_paid = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['appointment'], name='unique_appointment_invoice')
        ]

    def calculate_total(self):
        return Decimal(self.consultation_length) * (self.rate / Decimal('10'))

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.id} for {self.patient.username} - {self.get_patient_type_display()}"
