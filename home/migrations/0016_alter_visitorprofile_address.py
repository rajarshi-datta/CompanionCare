# Generated by Django 5.1.7 on 2025-03-31 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_customuser_address_visitorprofile_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitorprofile',
            name='address',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
