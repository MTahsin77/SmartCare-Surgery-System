import json
import os
import django
from django.conf import settings
from django.contrib.auth.hashers import make_password

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartcare.settings')
django.setup()

users = [
    {
        "model": "auth.user",
        "pk": 1,
        "fields": {
            "username": "admin",
            "password": "adminpassword",
            "email": "admin@example.com",
            "is_staff": True,
            "is_superuser": True
        }
    },
    {
        "model": "auth.user",
        "pk": 2,
        "fields": {
            "username": "doctor1",
            "password": "doctorpassword",
            "email": "doctor1@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    },
    {
        "model": "auth.user",
        "pk": 3,
        "fields": {
            "username": "doctor2",
            "password": "doctorpassword",
            "email": "doctor2@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    },
    {
        "model": "auth.user",
        "pk": 4,
        "fields": {
            "username": "nurse1",
            "password": "nursepassword",
            "email": "nurse1@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    },
    {
        "model": "auth.user",
        "pk": 5,
        "fields": {
            "username": "nurse2",
            "password": "nursepassword",
            "email": "nurse2@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    },
    {
        "model": "auth.user",
        "pk": 6,
        "fields": {
            "username": "user1",
            "password": "userpassword",
            "email": "user1@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    },
    {
        "model": "auth.user",
        "pk": 7,
        "fields": {
            "username": "user2",
            "password": "userpassword",
            "email": "user2@example.com",
            "is_staff": False,
            "is_superuser": False
        }
    }
]

# Hash the passwords
for user in users:
    user["fields"]["password"] = make_password(user["fields"]["password"])

# Write the fixture to a file
with open('initial_data.json', 'w') as f:
    json.dump(users, f, indent=4)

print("Fixture file 'initial_data.json' has been created.")
