import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from appointments.models import Appointment, Prescription, Invoice

User = get_user_model()

class SmartCareTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.patient = User.objects.create_user(username='testpatient', password='testpass123', user_type='patient')
        self.doctor = User.objects.create_user(username='testdoctor', password='testpass123', user_type='doctor')
        self.admin = User.objects.create_user(username='testadmin', password='testpass123', user_type='admin', is_staff=True)

    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'complex_password123',
            'password2': 'complex_password123',
            'user_type': 'patient'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login(self):
        response = self.client.post(reverse('login'), {
            'username': 'testpatient',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login

    def test_book_appointment(self):
        self.client.login(username='testpatient', password='testpass123')
        response = self.client.post(reverse('book_appointment'), {
            'doctor_or_nurse': 'doctor',
            'staff': self.doctor.id,
            'date': '2024-07-15',
            'time': '14:00',
            'reason': 'Test appointment'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after booking
        appointment = Appointment.objects.filter(patient=self.patient, doctor=self.doctor).first()
        self.assertIsNotNone(appointment)
        self.assertEqual(appointment.reason, 'Test appointment')
        
        if response.status_code != 302:
            print(response.context['form'].errors if 'form' in response.context else "No form in context")

    def test_issue_prescription(self):
        self.client.login(username='testdoctor', password='testpass123')
        appointment = Appointment.objects.create(
            patient=self.patient, 
            doctor=self.doctor, 
            date='2024-07-15', 
            time='14:00',
            reason='Test appointment'
        )
        response = self.client.post(reverse('issue_prescription', kwargs={'appointment_id': appointment.id}), {
            'medication': 'Test Med',
            'dosage': '1 pill daily',
            'instructions': 'Take with food'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after issuing prescription
        prescription = Prescription.objects.filter(patient=self.patient, doctor=self.doctor).first()
        self.assertIsNotNone(prescription)
        self.assertEqual(prescription.medication, 'Test Med')

    def test_generate_invoice(self):
        self.client.login(username='testadmin', password='testpass123')
        appointment = Appointment.objects.create(
            patient=self.patient, 
            doctor=self.doctor, 
            date='2024-07-15', 
            time='14:00',
            reason='Test appointment'
        )
        response = self.client.post(reverse('generate_invoice', kwargs={'appointment_id': appointment.id}), {
            'consultation_length': 30,
            'rate': 50,
            'patient_type': 'PRIVATE',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after generating invoice
        invoice = Invoice.objects.filter(patient=self.patient, appointment=appointment).first()
        self.assertIsNotNone(invoice)
        self.assertEqual(invoice.consultation_length, 30)
        self.assertEqual(invoice.rate, 50)
        
        if not invoice:
            print(response.context['form'].errors if 'form' in response.context else "No form in context")

    def test_unauthorized_access(self):
        self.client.login(username='testpatient', password='testpass123')
        response = self.client.get(reverse('doctor_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to unauthorized page