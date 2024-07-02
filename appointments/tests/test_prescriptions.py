from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from appointments.models import Prescription, Appointment
from appointments.forms import PrescriptionForm
from django.utils import timezone

User = get_user_model()

class PrescriptionTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.appointment = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date(),
            time='14:00',
            reason='Test appointment'
        )

    def test_prescription_model(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Test Med',
            dosage='1 pill daily',
            instructions='Take with food',
            is_repeatable=True
        )
        self.assertEqual(str(prescription), f"Test Med for {self.patient.username}")
        self.assertTrue(prescription.is_repeatable)

    def test_prescription_form_valid(self):
        form_data = {
            'medication': 'Test Med',
            'dosage': '1 pill daily',
            'instructions': 'Take with food',
            'is_repeatable': True
        }
        form = PrescriptionForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_prescription_form_invalid(self):
        form_data = {
            'medication': '',  # This field is required
            'dosage': '1 pill daily',
            'instructions': 'Take with food',
            'is_repeatable': True
        }
        form = PrescriptionForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_issue_prescription_view(self):
        self.client.login(username='doctor', password='testpass123')
        url = reverse('issue_prescription', args=[self.appointment.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            'medication': 'Test Med',
            'dosage': '1 pill daily',
            'instructions': 'Take with food',
            'is_repeatable': True
        }
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful submission
        self.assertTrue(Prescription.objects.filter(patient=self.patient, doctor=self.doctor).exists())

    def test_view_prescriptions(self):
        Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Test Med',
            dosage='1 pill daily',
            instructions='Take with food'
        )
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('view_prescriptions'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Med')

    def test_prescription_detail(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Test Med',
            dosage='1 pill daily',
            instructions='Take with food'
        )
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('prescription_detail', args=[prescription.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Med')
        self.assertContains(response, '1 pill daily')

    def test_unauthorized_access(self):
        other_user = User.objects.create_user(username='other', password='testpass123', user_type='patient')
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            medication='Test Med',
            dosage='1 pill daily',
            instructions='Take with food'
        )
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('prescription_detail', args=[prescription.id]))
        self.assertEqual(response.status_code, 302)