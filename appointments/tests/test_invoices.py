
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from appointments.models import Appointment, Invoice
from appointments.forms import InvoiceForm
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import IntegrityError

User = get_user_model()

class InvoiceTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.doctor = User.objects.create_user(username='doctor', password='testpass123', user_type='doctor')
        self.patient = User.objects.create_user(username='patient', password='testpass123', user_type='patient')
        self.admin = User.objects.create_user(username='admin', password='testpass123', user_type='admin')
        self.appointment1 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date(),
            time='14:00',
            reason='Test appointment 1'
        )
        self.appointment2 = Appointment.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            date=timezone.now().date(),
            time='15:00',
            reason='Test appointment 2'
        )

    def test_invoice_creation(self):
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE'
        )
        self.assertEqual(invoice.total_amount, Decimal('100.00'))
        self.assertEqual(str(invoice), f"Invoice {invoice.id} for {self.patient.username} - Private")

    def test_invoice_form_valid_data(self):
        form_data = {
            'consultation_length': 30,
            'rate': '50.00',
            'patient_type': 'NHS'
        }
        form = InvoiceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invoice_form_invalid_data(self):
        form_data = {
            'consultation_length': 5,  # Invalid: less than 10
            'rate': '-50.00',  # Invalid: negative rate
            'patient_type': 'INVALID'  # Invalid: not a valid choice
        }
        form = InvoiceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('consultation_length', form.errors)
        self.assertIn('rate', form.errors)
        self.assertIn('patient_type', form.errors)

    def test_generate_invoice_view(self):
        self.client.login(username='doctor', password='testpass123')
        response = self.client.post(reverse('generate_invoice', args=[self.appointment1.id]), {
            'consultation_length': 20,
            'rate': '50.00',
            'patient_type': 'PRIVATE'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        self.assertTrue(Invoice.objects.filter(appointment=self.appointment1).exists())

    def test_view_invoice(self):
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=30,
            rate=Decimal('50.00'),
            patient_type='NHS'
        )
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('view_invoice', args=[invoice.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '150.00')

    def test_admin_invoices(self):
        Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE',
            payment_status='PAID'
        )
        Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment2,
            consultation_length=30,
            rate=Decimal('40.00'),
            patient_type='NHS',
            payment_status='SENT_TO_NHS'
        )
        self.client.login(username='admin', password='testpass123')
        response = self.client.get(reverse('admin_invoices'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '220.00')  # Total turnover
        self.assertContains(response, '120.00')  # NHS charges
        self.assertContains(response, '100.00')  # Private payments

    def test_unauthorized_access(self):
        other_user = User.objects.create_user(username='other', password='testpass123', user_type='patient')
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE'
        )
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('view_invoice', args=[invoice.id]))
        self.assertEqual(response.status_code, 302)  # Should redirect to unauthorized access page

    def test_invoice_model_validation(self):
        with self.assertRaises(ValidationError):
            invoice = Invoice(
                patient=self.patient,
                appointment=self.appointment1,
                consultation_length=5,  # Invalid: less than 10
                rate=Decimal('50.00'),
                patient_type='PRIVATE'
            )
            invoice.full_clean()

    def test_duplicate_invoice_prevention(self):
        Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE'
    )
    with self.assertRaises(IntegrityError):
        Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=30,
            rate=Decimal('40.00'),
            patient_type='NHS'
        )

    def test_patient_invoices_view(self):
        Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE'
        )
        self.client.login(username='patient', password='testpass123')
        response = self.client.get(reverse('patient_invoices'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Private')
        self.assertContains(response, '100.00')

    def test_invoice_update(self):
        invoice = Invoice.objects.create(
            patient=self.patient,
            appointment=self.appointment1,
            consultation_length=20,
            rate=Decimal('50.00'),
            patient_type='PRIVATE'
        )
        self.client.login(username='admin', password='testpass123')
        response = self.client.post(reverse('update_invoice', args=[invoice.id]), {
            'consultation_length': 30,
            'rate': '60.00',
            'patient_type': 'NHS'
        })
        self.assertEqual(response.status_code, 302)  # Should redirect after successful update
        invoice.refresh_from_db()
        self.assertEqual(invoice.consultation_length, 30)
        self.assertEqual(invoice.rate, Decimal('60.00'))
        self.assertEqual(invoice.patient_type, 'NHS')
        self.assertEqual(invoice.total_amount, Decimal('180.00'))