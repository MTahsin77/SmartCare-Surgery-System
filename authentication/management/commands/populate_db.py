
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from authentication.models import User

class Command(BaseCommand):
    help = 'Populate the database with initial data'

    def handle(self, *args, **kwargs):
        users = [
            {"username": "admin", "password": "adminpassword", "email": "admin@example.com", "is_staff": True, "is_superuser": True, "user_type": "admin"},
            {"username": "doctor1", "password": "doctorpassword", "email": "doctor1@example.com", "is_staff": False, "is_superuser": False, "user_type": "doctor"},
            {"username": "doctor2", "password": "doctorpassword", "email": "doctor2@example.com", "is_staff": False, "is_superuser": False, "user_type": "doctor"},
            {"username": "nurse1", "password": "nursepassword", "email": "nurse1@example.com", "is_staff": False, "is_superuser": False, "user_type": "nurse"},
            {"username": "nurse2", "password": "nursepassword", "email": "nurse2@example.com", "is_staff": False, "is_superuser": False, "user_type": "nurse"},
            {"username": "user1", "password": "userpassword", "email": "user1@example.com", "is_staff": False, "is_superuser": False, "user_type": "patient"},
            {"username": "user2", "password": "userpassword", "email": "user2@example.com", "is_staff": False, "is_superuser": False, "user_type": "patient"},
        ]

        for user_data in users:
            if not User.objects.filter(username=user_data['username']).exists():
                user_data['password'] = make_password(user_data['password'])
                User.objects.create(**user_data)
                self.stdout.write(self.style.SUCCESS(f"User {user_data['username']} created successfully."))
                self.stdout.write(self.style.WARNING(f"User {user_data['username']} already exists."))
