from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from appointments.models import Appointment
from django.utils import timezone

User = get_user_model()

class ForwardPatientTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.doctor1 = User.objects.create_user(username='doctor1', password='testpass123', user_type='doctor')
        self.doctor2 = User.objects.create_user(username='doctor2', password='testpass123', user_type='doctor')
        self.nurse = User.objects.create_user(username='nurse', password='testpass123', user_type='nurse')
        self.admin = User.objects.create_user(username='admin', password='testpass123', user_type='admin', is_staff=True)

        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor1,
            date=timezone.now().date(),
            time='14:00',
            reason='Test appointment',
            latitude=51.5074,
            longitude=-0.1278
        )

    def test_forward_patient_view_get(self):
        self.client.login(username='doctor1', password='testpass123')
        response = self.client.get(reverse('forward_patient', args=[self.appointment.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'appointments/forward_patient.html')

    def test_forward_patient_view_post_success(self):
        self.client.login(username='doctor1', password='testpass123')
        response = self.client.post(reverse('forward_patient', args=[self.appointment.id]), {
            'new_doctor': self.doctor2.id
        })
        self.assertRedirects(response, reverse('view_appointments'))
        
        # Check that a new appointment was created
        new_appointment = Appointment.objects.filter(patient=self.patient, doctor=self.doctor2).first()
        self.assertIsNotNone(new_appointment)
        self.assertTrue(new_appointment.reason.startswith('Forwarded:'))

        # Check that the original appointment was updated
        original_appointment = Appointment.objects.get(id=self.appointment.id)
        self.assertTrue(original_appointment.is_forwarded)
        self.assertEqual(original_appointment.forwarded_to, new_appointment)

    def test_forward_patient_view_post_invalid_doctor(self):
        self.client.login(username='doctor1', password='testpass123')
        response = self.client.post(reverse('forward_patient', args=[self.appointment.id]), {
            'new_doctor': 9999  # Non-existent doctor ID
        })
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Selected doctor does not exist.')

    def test_forward_patient_view_unauthorized(self):
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('forward_patient', args=[self.appointment.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect to unauthorized page

    def test_nurse_can_forward_patient(self):
        self.client.login(username='nurse', password='testpass123')
        response = self.client.post(reverse('forward_patient', args=[self.appointment.id]), {
            'new_doctor': self.doctor2.id
        })
        self.assertRedirects(response, reverse('view_appointments'))

    def test_admin_can_forward_patient(self):
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('forward_patient', args=[self.appointment.id]), {
            'new_doctor': self.doctor2.id
        })
        self.assertRedirects(response, reverse('view_appointments'))