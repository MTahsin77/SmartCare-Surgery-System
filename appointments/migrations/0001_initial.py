# Generated by Django 5.0.6 on 2024-07-08 13:05

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('reason', models.TextField(blank=True, default='General checkup', help_text='Reason for the appointment')),
                ('address', models.CharField(blank=True, help_text='Address where the appointment will take place', max_length=255, null=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('COMPLETED', 'Completed'), ('FORWARDED', 'Forwarded'), ('CANCELED', 'Canceled')], default='SCHEDULED', max_length=10)),
                ('doctor_or_nurse', models.CharField(blank=True, choices=[('doctor', 'Doctor'), ('nurse', 'Nurse')], max_length=10, null=True)),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments_as_doctor', to=settings.AUTH_USER_MODEL)),
                ('nurse', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointments_as_nurse', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointments_as_patient', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CompletedForwardedCanceled',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_changed', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='appointments.appointment')),
                ('changed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient_type', models.CharField(choices=[('NHS', 'NHS'), ('PRIVATE', 'Private')], max_length=7)),
                ('consultation_length', models.PositiveIntegerField(help_text='Length of consultation in minutes')),
                ('rate', models.DecimalField(decimal_places=2, help_text='Rate per 10 minutes', max_digits=6)),
                ('total_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_status', models.CharField(choices=[('PENDING', 'Pending'), ('PAID', 'Paid'), ('SENT_TO_NHS', 'Sent to NHS')], default='PENDING', max_length=15)),
                ('date_issued', models.DateTimeField(default=django.utils.timezone.now)),
                ('date_paid', models.DateTimeField(blank=True, null=True)),
                ('appointment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='appointments.appointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invoices', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medication', models.CharField(max_length=100)),
                ('dosage', models.CharField(max_length=100)),
                ('instructions', models.TextField()),
                ('date_prescribed', models.DateTimeField(auto_now_add=True)),
                ('is_repeatable', models.BooleanField(default=False)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to='appointments.appointment')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescribed', to=settings.AUTH_USER_MODEL)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prescriptions', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(
            model_name='invoice',
            constraint=models.UniqueConstraint(fields=('appointment',), name='unique_appointment_invoice'),
        ),
    ]
