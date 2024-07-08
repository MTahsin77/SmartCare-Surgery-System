from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from appointments.models import Appointment
from appointments.forms import AppointmentForm
from django.core.exceptions import ValidationError

User = get_user_model()

class AppointmentModelTest(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.nurse = User.objects.create_user(username='nurse', password='testpass123', user_type='nurse')
        self.future_date = timezone.now().date() + timezone.timedelta(days=1)

    def test_appointment_creation(self):
        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=self.future_date,
            time='14:00',
            reason='Test appointment',
            address='123 Test St'
        )
        self.assertTrue(isinstance(appointment, Appointment))
        self.assertEqual(str(appointment), f'Appointment with {self.doctor} on {self.future_date} at 14:00:00')
    
    def test_appointment_validation(self):
        with self.assertRaises(ValidationError):
            appointment = Appointment(
                patient=self.patient,
                doctor=self.doctor,
                date=timezone.now().date() - timezone.timedelta(days=1),
                time='14:00',
                reason='Past appointment'
            )
            appointment.full_clean()

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.create_calendar_event')
    def test_sync_with_google_calendar(self, mock_create_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_create_event.return_value = {'id': 'test_event_id'}

        appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=self.future_date,
            time='14:00',
            reason='Test appointment'
        )
        appointment.sync_with_google_calendar()

        mock_get_service.assert_called_once()
        mock_create_event.assert_called_once()
        self.assertEqual(appointment.google_calendar_event_id, 'test_event_id')

class AppointmentViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.book_appointment_url = reverse('book_appointment')
        self.future_date = timezone.now().date() + timezone.timedelta(days=1)

    def test_book_appointment_view_get(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(self.book_appointment_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/book_appointment.html')

    @patch('appointments.forms.AppointmentForm.save')
    @patch('appointments.views.AppointmentForm.is_valid')
    @patch('appointments.models.Appointment.sync_with_google_calendar')
    def test_book_appointment_view_post(self, mock_sync, mock_is_valid, mock_save):
        mock_is_valid.return_value = True
        mock_sync.return_value = None
        mock_save.return_value = Appointment(patient=self.patient, doctor=self.doctor)
        
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(self.book_appointment_url, {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': self.future_date,
            'time': '14:00',
            'reason': 'Test appointment',
            'address': '123 Test St',
            'latitude': 40.7128,
            'longitude': -74.0060
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful booking
        mock_save.assert_called_once()

    def test_book_appointment_view_post_invalid_form(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.post(self.book_appointment_url, {})  # Empty data
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertContains(response, "There was an error with your form submission. Please check the errors below.")

class AppointmentFormTest(TestCase):
    def setUp(self):
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.future_date = timezone.now().date() + timezone.timedelta(days=1)

    def test_valid_form(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': self.future_date,
            'time': '14:00',
            'reason': 'Test appointment',
            'address': '123 Test St',
            'latitude': 40.7128,
            'longitude': -74.0060
        }
        form = AppointmentForm(data=form_data)
        form.fields['staff'].queryset = User.objects.filter(user_type='doctor')
        if not form.is_valid():
            print(f"Form errors: {form.errors}")
        self.assertTrue(form.is_valid())
        
        # Test that the form creates a valid Appointment instance
        appointment = form.save(commit=False)
        appointment.patient = self.patient
        try:
            appointment.full_clean()
        except ValidationError as e:
            self.fail(f"Appointment validation failed: {e}")

    def test_invalid_form(self):
        form_data = {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': timezone.now().date() - timezone.timedelta(days=1),  # Past date
            'time': '14:00',
            'reason': 'Test appointment',
            'address': '123 Test St'
        }
        form = AppointmentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date', form.errors)