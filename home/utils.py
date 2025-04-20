from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.conf import settings
import random

User = get_user_model()

def send_verification_email(user, verification_code):
    """Send an email with the verification code."""
    subject = "Your Verification Code - Companion Care"
    message = render_to_string("email_verification.html", {"code": verification_code, "user": user})

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return str(random.randint(100000, 999999))
