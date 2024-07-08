from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from .forms import AppointmentForm
from .models import Appointment
from authentication.models import User

class AppointmentFormTest(TestCase):

    def setUp(self):
        self.patient = User.objects.create_user(username='patient', password='patient123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='doctor123', user_type='doctor')

    def test_valid_form(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        form = AppointmentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_date(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() - timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)

    def test_invalid_time_format(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': 'invalid-time',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('time', form.errors)

    def test_missing_staff(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': '',
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('staff', form.errors)

    def test_time_slot_already_booked(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date() + timezone.timedelta(days=1),
            time=timezone.datetime.strptime('10:00', '%H:%M').time(),
            reason='Existing Checkup',
            address='123 Main St'
        )
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'New Checkup',
            'address': '123 Main St'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

class AppointmentViewTest(TestCase):

    def setUp(self):
        self.patient = User.objects.create_user(username='patient', password='patient123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='doctor123', user_type='doctor')
        self.client.login(username='patient', password='patient123')

    def test_get_book_appointment_page(self):
        response = self.client.get(reverse('book_appointment'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/book_appointment.html')

    def test_post_valid_appointment(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        response = self.client.post(reverse('book_appointment'), data=form_data)
        self.assertEqual(response.status_code, 302)  # Should redirect to view_appointments
        self.assertEqual(Appointment.objects.count(), 1)

    def test_post_invalid_appointment(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': '',
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'Checkup',
            'address': '123 Main St'
        }
        response = self.client.post(reverse('book_appointment'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'staff', 'Please select a doctor')
        self.assertEqual(Appointment.objects.count(), 0)

    def test_appointment_time_slot_already_booked(self):
        Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date() + timezone.timedelta(days=1),
            time=timezone.datetime.strptime('10:00', '%H:%M').time(),
            reason='Existing Checkup',
            address='123 Main St'
        )
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': (timezone.now().date() + timezone.timedelta(days=1)).strftime('%Y-%m-%d'),
            'time': '10:00',
            'reason': 'New Checkup',
            'address': '123 Main St'
        }
        response = self.client.post(reverse('book_appointment'), data=form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', None, 'This time slot is already booked')
        self.assertEqual(Appointment.objects.count(), 1)
