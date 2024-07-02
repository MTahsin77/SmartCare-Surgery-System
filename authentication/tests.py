from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from authentication.models import UserProfile
from django.utils import timezone

User = get_user_model()

class AuthenticationTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.nurse = User.objects.create_user(username='nurse', password='testpass123', user_type='nurse')
        self.admin = User.objects.create_user(username='admin', password='testpass123', user_type='admin')

        UserProfile.objects.create(user=self.patient)
        UserProfile.objects.create(user=self.doctor)
        UserProfile.objects.create(user=self.nurse)
        UserProfile.objects.create(user=self.admin)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'newuser@example.com',
            'user_type': 'patient'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'patient',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertTrue('_auth_user_id' in self.client.session)

    def test_user_logout(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)  # Redirect after logout
        self.assertFalse('_auth_user_id' in self.client.session)

    def test_patient_dashboard_access(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('patient_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_doctor_dashboard_access(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_nurse_dashboard_access(self):
        self.client.login(username='nurse', password='testpass123')
        response = self.client.get(reverse('nurse_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_dashboard_access(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to unauthorized page

    def test_book_appointment(self):
        self.client.login(username='patient', password='testpass123')
        doctor = User.objects.get(username='doctor')
        response = self.client.post(reverse('book_appointment'), {
            'doctor': doctor.id,
            'date': timezone.now().date(),
            'time': '14:00',
            'reason': 'Test appointment'
        })
        if response.status_code != 302:
            print(f"Response content: {response.content.decode()}")  
        self.assertEqual(response.status_code, 302)  
        self.assertTrue(Appointment.objects.filter(patient=self.patient, doctor=doctor).exists())

    def test_list_appointments(self):
        self.client.login(username='patient', password='testpass123')
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date(),
            time='14:00',
            reason='Test appointment'
        )
        response = self.client.get(reverse('list_appointments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test appointment')

    def test_profile_update(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(reverse('profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com',
            'address': '123 Test St'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after update
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.first_name, 'Updated')
        self.assertEqual(self.patient.last_name, 'Name')
        self.assertEqual(self.patient.email, 'updated@example.com')
        self.assertEqual(self.patient.userprofile.address, '123 Test St')
