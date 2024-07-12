from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
    )
    PATIENT_TYPE_CHOICES = (
        ('NHS', 'NHS Patient'),
        ('PRIVATE', 'Private Patient'),
    )
    DOCTOR_SPECIALTIES = (
        ('EYE', 'Eye Specialist'),
        ('GYN', 'Gynecologist'),
        ('ORT', 'Orthopedic'),
        ('PED', 'Pediatrician'),
        ('PSY', 'Psychiatrist'),
        ('RAD', 'Radiologist'),
        ('URO', 'Urologist'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    patient_type = models.CharField(max_length=7, choices=PATIENT_TYPE_CHOICES, default='NHS')
    specialty = models.CharField(max_length=3, choices=DOCTOR_SPECIALTIES, null=True, blank=True)

    def is_patient(self):
        return self.user_type == 'patient'

    def is_doctor(self):
        return self.user_type == 'doctor'

    def is_nurse(self):
        return self.user_type == 'nurse'

    def is_admin(self):
        return self.user_type == 'admin'

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"Profile for {self.user.username}"


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        instance.userprofile.save()

class PendingRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending registration for {self.user.username}"

class GPDetails(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
