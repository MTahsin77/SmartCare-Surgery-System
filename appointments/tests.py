from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Appointment, Prescription
from datetime import datetime, timedelta
from django.utils import timezone

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
            date=timezone.now().date() + timedelta(days=1),
            time='10:00',
            reason='Test appointment'
        )

    def test_book_appointment(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(reverse('book_appointment'), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '14:00',
            'reason': 'New test appointment'
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
        self.assertRedirects(response, reverse('view_appointments'))
        self.assertEqual(Appointment.objects.count(), 0)

    def test_reschedule_appointment(self):
        self.client.login(username='doctor', password='testpass123')
        new_date = timezone.now().date() + timedelta(days=3)
        response = self.client.post(reverse('reschedule_appointment', args=[self.appointment.id]), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': new_date.strftime('%Y-%m-%d'),
            'time': '15:00',
            'reason': 'Rescheduled appointment'
        })
        self.assertRedirects(response, reverse('view_appointments'))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.date, new_date)
        self.assertEqual(self.appointment.time.strftime('%H:%M'), '15:00')

    def test_complete_appointment(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.post(reverse('complete_appointment', args=[self.appointment.id]))
        self.assertRedirects(response, reverse('view_appointments'))
        self.appointment.refresh_from_db()
        self.assertTrue(self.appointment.is_completed)

    def test_appointment_detail(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('appointment_detail', args=[self.appointment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test appointment')

    def test_issue_prescription(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.post(reverse('issue_prescription', args=[self.appointment.id]), {
            'medication': 'Test Med',
            'dosage': '1 pill daily',
            'instructions': 'Take with food'
        })
        print('Response status code:', response.status_code)
        print('Response URL:', response.url)
        self.assertRedirects(response, reverse('appointment_detail', args=[self.appointment.id]))
        self.assertEqual(Prescription.objects.count(), 1)
        prescription = Prescription.objects.first()
        self.assertEqual(prescription.medication, 'Test Med')
        self.assertEqual(prescription.dosage, '1 pill daily')
        self.assertEqual(prescription.instructions, 'Take with food')

    def test_load_staff(self):
        response = self.client.get(reverse('ajax_load_staff'), {'doctor_or_nurse': 'doctor'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.doctor.username)
        self.assertTemplateUsed(response, 'appointments/staff_dropdown_list_options.html')

    def test_get_available_slots(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.get(reverse('get_available_slots'), {'date': '2024-07-01', 'doctor_id': self.doctor.id})
        self.assertEqual(response.status_code, 200)
        self.assertIn('09:00', response.json())

    def test_unauthorized_access(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('complete_appointment', args=[self.appointment.id]))
        self.assertRedirects(response, reverse('unauthorized_access'))

        self.client.login(username='nurse', password='testpass123')
        response = self.client.get(reverse('issue_prescription', args=[self.appointment.id]))
        self.assertRedirects(response, reverse('unauthorized_access'))

    def test_appointment_conflict(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(reverse('book_appointment'), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': self.appointment.date,
            'time': self.appointment.time,
            'reason': 'Conflicting appointment'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This time slot is already booked')

    def test_past_date_appointment(self):
        self.client.login(username='patient', password='testpass123')
        past_date = timezone.now().date() - timedelta(days=1)
        response = self.client.post(reverse('book_appointment'), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': past_date.strftime('%Y-%m-%d'),
            'time': '14:00',
            'reason': 'Past appointment'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Appointment date cannot be in the past')
