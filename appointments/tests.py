# tests.py

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Appointment
from datetime import datetime, timedelta, time

User = get_user_model()

class AppointmentTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.nurse = User.objects.create_user(username='nurse', password='testpass123', user_type='nurse')
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=datetime.now().date() + timedelta(days=1),
            time=time(10, 0),
            reason='Test appointment',
            is_completed=False  
        )

    def test_book_appointment(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(reverse('book_appointment'), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (datetime.now().date() + timedelta(days=2)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'reason': 'New test appointment',
            'address': 'Test Address'
        })
        self.assertRedirects(response, reverse('view_appointments'))
        self.assertEqual(Appointment.objects.count(), 2)

    def test_view_appointments(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('view_appointments'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test appointment')

    def test_cancel_appointment(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(reverse('cancel_appointment', args=[self.appointment.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after cancellation
        self.assertFalse(Appointment.objects.filter(id=self.appointment.id).exists())

    def test_complete_appointment(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.post(reverse('complete_appointment', args=[self.appointment.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after completion
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.is_completed)

    def test_reschedule_appointment(self):
        self.client.login(username='doctor', password='testpass123')
        new_date = datetime.now().date() + timedelta(days=3)
        response = self.client.post(reverse('reschedule_appointment', args=[self.appointment.id]), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': new_date.strftime('%Y-%m-%d'),
            'time': '15:00',
            'reason': 'Rescheduled appointment',
            'address': 'Test Address'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after rescheduling
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.date, new_date)
        self.assertEqual(self.appointment.time, time(15, 0))  # Compare with a datetime.time object
