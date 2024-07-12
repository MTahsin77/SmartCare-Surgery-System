from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from decimal import Decimal
from authentication.models import User

class Appointment(models.Model):
    STAFF_CHOICES = [
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse')
    ]
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('COMPLETED', 'Completed'),
        ('CANCELED', 'Canceled')
    ]
    APPOINTMENT_TYPES = [
        ('SURGERY', 'Surgery'),
        ('GENERAL_CHECKUP', 'General Checkup'),
        ('DENTAL', 'Dental Consultation'),
        ('PHYSICAL_THERAPY', 'Physical Therapy'),
        ('DERMATOLOGY', 'Dermatology'),
        ('CARDIOLOGY', 'Cardiology'),
        ('NEUROLOGY', 'Neurology'),
    ]
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments_as_patient')
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='appointments_as_doctor', null=True, blank=True)
    nurse = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='appointments_as_nurse', null=True, blank=True)
    date = models.DateField()
    time = models.TimeField(default="12:00:00")
    end_time = models.TimeField()
    reason = models.TextField(help_text="Reason for the appointment", blank=True, default="General checkup")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='SCHEDULED')
    doctor_or_nurse = models.CharField(max_length=10, choices=STAFF_CHOICES, null=True, blank=True)
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPES, default='GENERAL_CHECKUP')

    def update_status(self, new_status):
        if new_status in dict(self.STATUS_CHOICES):
            self.status = new_status
            self.save(update_fields=['status'])
        else:
            raise ValueError(f"Invalid status: {new_status}")
        
    def save(self, *args, **kwargs):
        if not self.end_time:
            self.end_time = (datetime.combine(self.date, self.time) + timedelta(minutes=10)).time()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_appointment_type_display()} for {self.patient} on {self.date} at {self.time}"

class Prescription(models.Model):
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    doctor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='prescriptions', on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, related_name='prescriptions', on_delete=models.CASCADE)  # Added this line
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()
    date_prescribed = models.DateTimeField(auto_now_add=True)
    is_repeatable = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.medication} prescribed to {self.patient.get_full_name()} by {self.doctor.get_full_name()}'

class PrescriptionRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescription_requests')
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE)
    request_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Prescription request for {self.patient.username} - {self.prescription.medication}"

class Fee(models.Model):
    PATIENT_TYPE_CHOICES = [
        ('ALL', 'All Patients'),
        ('NHS', 'NHS Patients'),
        ('PRIVATE', 'Private Patients'),
    ]
    title = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    patient_type = models.CharField(max_length=10, choices=PATIENT_TYPE_CHOICES, default='ALL')

    def __str__(self):
        return f"{self.title} - £{self.amount} ({self.get_patient_type_display()})"

class DefaultRate(models.Model):
    RATE_TYPES = [
        ('NHS_PATIENT', 'NHS Patient'),
        ('PRIVATE_PATIENT', 'Private Patient'),
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
    ]
    rate_type = models.CharField(max_length=20, choices=RATE_TYPES, unique=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.get_rate_type_display()} Default Rate: £{self.amount}"
    
class Rate(models.Model):
    RATE_TYPES = [
        ('NHS_PATIENT', 'NHS Patient'),
        ('PRIVATE_PATIENT', 'Private Patient'),
        ('DOCTOR', 'Doctor'),
        ('NURSE', 'Nurse'),
    ]
    rate_type = models.CharField(max_length=20, choices=RATE_TYPES, unique=True)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.get_rate_type_display()} Rate: £{self.amount}"

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
    fees = models.ManyToManyField(Fee, related_name='invoices')

    def calculate_total(self):
        base_amount = Decimal(self.consultation_length) * (self.rate / Decimal('10'))
        if self.id:  # Only include fees if the invoice has been saved
            fee_amount = sum(fee.amount for fee in self.fees.all())
        else:
            fee_amount = Decimal('0.00')
        return base_amount + fee_amount

    def save(self, *args, **kwargs):
        if not self.id:
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Invoice {self.id} for {self.patient.username} - {self.get_patient_type_display()}"


class CompletedForwardedCanceled(models.Model):
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    date_changed = models.DateTimeField(default=timezone.now)
    reason = models.TextField(blank=True, null=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"CFC: {self.appointment} - {self.appointment.get_status_display()}"
