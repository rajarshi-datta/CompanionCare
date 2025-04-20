from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings 


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ("resident", "Resident"),
        ("caregiver", "Caregiver"),
        ("visitor", "Visitor"),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default="resident")
    is_resident = models.BooleanField(default=False)
    is_visitor = models.BooleanField(default=False)  
    email = models.EmailField()
    address = models.CharField(max_length=255, blank=True, null=True)
class CaregiverProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="caregiver_profile")
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    experience = models.TextField(blank=True, null=True)
    qualifications = models.TextField(blank=True, null=True)
    availability = models.CharField(max_length=255, blank=True, null=True)  
    location = models.CharField(max_length=255, blank=True, null=True)  
    is_active = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6, blank=True, null=True)
    is_verified = models.BooleanField(default=False)  
    certifications = models.TextField(blank=True, null=True)
    specialization = models.CharField(max_length=255, blank=True, null=True)
    availability = models.CharField(
        max_length=50,
        choices=[("full-time", "Full-Time"), ("part-time", "Part-Time"), ("on-call", "On-Call")],
        default="full-time"
    )
    service_start_time = models.TimeField(blank=True, null=True)  # New Field
    service_end_time = models.TimeField(blank=True, null=True)  # New Field
    languages = models.CharField(max_length=255, blank=True, null=True)  # New Field
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)  # New Field
    bio = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="caregiver_pics/", blank=True, null=True)

    def str(self):
        return f"Caregiver Profile: {self.user.username}"

class ResidentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="resident_profile")  # ✅ Corrected user field
    name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=[("male", "Male"), ("female", "Female")])
    room = models.CharField(max_length=10)
    phone = models.CharField(max_length=15, blank=True, null=True) 
    photo = models.ImageField(upload_to="resident_photos/", blank=True, null=True)
    meal = models.CharField(max_length=50, blank=True, null=True)
    assistance = models.CharField(max_length=100, blank=True, null=True)
    visit_schedule = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact = models.CharField(max_length=100, null=True, blank=True)
    emergency_phone = models.CharField(max_length=15, null=True, blank=True) 
    conditions = models.CharField(max_length=255, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medications = models.TextField(blank=True, null=True)
    medication_schedule = models.CharField(max_length=50, blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    doctor_phone = models.CharField(max_length=15, blank=True, null=True)
    reminder_time = models.TimeField(blank=True, null=True)  # ✅ Corrected field
    reminder_message = models.TextField(default="Take the medicine")  # ✅ Default reminder message
    last_sent = models.DateTimeField(null=True, blank=True)


    def str(self):
        return f"Resident Profile: {self.user.username}"
class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="messages")
    title = models.CharField(max_length=255)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.user.username}: {self.title}"
from django.db import models

from django.utils.timezone import now

class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ Correct reference
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255, default="Untitled Notification") 
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.user.username}"

from django.db import models
from django.contrib.auth.models import User

class VisitorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='visitor_profiles/', default='default_profile.jpg', blank=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    address=models.CharField(max_length=255,blank=True,null=False)
    def __str__(self):
        return self.user.username
class MeetingRequest(models.Model):
    visitor = models.ForeignKey(VisitorProfile, on_delete=models.CASCADE, related_name="meeting_requests")
    resident = models.ForeignKey(ResidentProfile, on_delete=models.CASCADE, related_name="meeting_requests")
    request_date = models.DateTimeField(default=now)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.TimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("accepted", "Accepted"), ("declined", "Declined")],
        default="pending",
    )

    def __str__(self):
        return f"{self.visitor.user.username} → {self.resident.user.username} ({self.status})"
