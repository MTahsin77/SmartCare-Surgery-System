from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('nurse', 'Nurse'),
        ('admin', 'Admin'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='patient')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='authentication_user_set', 
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='authentication_user_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

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

class PendingRegistration(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pending registration for {self.user.username}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, null=True) 
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class GPDetails(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"