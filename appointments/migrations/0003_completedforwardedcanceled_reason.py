# Generated by Django 5.0.6 on 2024-07-08 22:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0002_remove_appointment_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='completedforwardedcanceled',
            name='reason',
            field=models.TextField(blank=True, null=True),
        ),
    ]
