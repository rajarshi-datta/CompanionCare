# Generated by Django 5.1.7 on 2025-03-26 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_message_is_read'),
    ]

    operations = [
        migrations.AddField(
            model_name='residentprofile',
            name='last_sent',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
