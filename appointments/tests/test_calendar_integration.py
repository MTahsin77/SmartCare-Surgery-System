from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from unittest.mock import patch, MagicMock
from appointments.models import Appointment

User = get_user_model()

class AppointmentCalendarIntegrationTest(TransactionTestCase):
    def setUp(self):
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.appointment_data = {
            'patient': self.patient,
            'doctor': self.doctor,
            'date': timezone.now().date(),
            'time': timezone.now().time(),
            'reason': 'Test appointment',
        }

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.create_calendar_event')
    def test_create_appointment_with_calendar_event(self, mock_create_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_create_event.return_value = {'id': 'test_event_id'}

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.sync_with_google_calendar()

        mock_get_service.assert_called_once()
        mock_create_event.assert_called_once()
        self.assertEqual(appointment.google_calendar_event_id, 'test_event_id')

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.update_calendar_event')
    def test_update_appointment_with_calendar_event(self, mock_update_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.google_calendar_event_id = 'existing_event_id'
        appointment.reason = 'Updated reason'
        appointment.save()
        appointment.sync_with_google_calendar()

        mock_get_service.assert_called()
        mock_update_event.assert_called_once()

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.delete_calendar_event')
    def test_delete_appointment_with_calendar_event(self, mock_delete_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.google_calendar_event_id = 'existing_event_id'
        appointment.delete()

        mock_get_service.assert_called_once()
        mock_delete_event.assert_called_once_with(mock_service, 'existing_event_id')

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.create_calendar_event')
    def test_create_appointment_handles_api_error(self, mock_create_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_create_event.side_effect = Exception("API Error")

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.sync_with_google_calendar()

        mock_get_service.assert_called_once()
        mock_create_event.assert_called_once()
        self.assertIsNone(appointment.google_calendar_event_id)

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.update_calendar_event')
    def test_update_appointment_handles_api_error(self, mock_update_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_update_event.side_effect = Exception("API Error")

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.google_calendar_event_id = 'existing_event_id'
        appointment.reason = 'Updated reason'
        appointment.save()
        appointment.sync_with_google_calendar()

        mock_get_service.assert_called()
        mock_update_event.assert_called_once()
        self.assertEqual(Appointment.objects.get(id=appointment.id).reason, 'Updated reason')

    @patch('appointments.models.get_calendar_service')
    @patch('appointments.models.delete_calendar_event')
    def test_delete_appointment_handles_api_error(self, mock_delete_event, mock_get_service):
        mock_service = MagicMock()
        mock_get_service.return_value = mock_service
        mock_delete_event.side_effect = Exception("API Error")

        appointment = Appointment.objects.create(**self.appointment_data)
        appointment.google_calendar_event_id = 'existing_event_id'
        appointment.delete()

        mock_get_service.assert_called_once()
        mock_delete_event.assert_called_once_with(mock_service, 'existing_event_id')
        self.assertFalse(Appointment.objects.filter(id=appointment.id).exists())