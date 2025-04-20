from django.shortcuts import render, redirect,get_object_or_404
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import ResidentProfile
from .models import Message, Notification, ResidentProfile
from django.shortcuts import render
from django.utils.timezone import now
from django.http import JsonResponse
from twilio.rest import Client
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import ResidentProfile
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime, now, make_aware, is_naive
from django.utils.encoding import force_str
from .utils import generate_verification_code
from .models import VisitorProfile

from .utils import send_verification_email 

# ✅ Import models correctly
from .models import CaregiverProfile, CustomUser, ResidentProfile  
from .forms import UserSignupForm, CaregiverSignupForm, ResidentProfileForm  

def home(request):
    return render(request, "index.html", {"media_url": settings.MEDIA_URL})

# ✅ User Signup
def user_signup(request):
    if request.method == "POST":
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("resident_dashboard")
        else:
            messages.error(request, "Error in form submission.")
    else:
        form = UserSignupForm()
    return render(request, "user_signup.html", {"form": form})


def caregiver_signup(request):
    if request.method == "POST":
        form = CaregiverSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            # ✅ Set user as inactive until email verification
            user.is_active = False
            user.user_type = "caregiver"

            # ✅ Split full_name into first_name & last_name
            full_name = form.cleaned_data["full_name"]
            name_parts = full_name.split(" ", 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ""

            user.save()

            # ✅ Generate verification code
            verification_code = generate_verification_code()

            # ✅ Create Caregiver Profile with verification code
            caregiver_profile = CaregiverProfile.objects.create(
                user=user,
                experience=form.cleaned_data["experience"],
                qualifications=form.cleaned_data["qualifications"],
                availability=form.cleaned_data["availability"],
                location=form.cleaned_data["location"],
                verification_code=verification_code,  # ✅ Store verification code here
            )

            # ✅ Send email verification
            send_verification_email(user, verification_code)  # ✅ Pass email & code

            messages.success(request, "Your account has been created! Please check your email to verify your account.")
            return redirect("verify_code")

    else:
        form = CaregiverSignupForm()

    return render(request, "caregiversignup.html", {"form": form})


# ✅ Caregiver Login
def caregiver_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user and user.is_active:
                if user.user_type == "caregiver":
                    login(request, user)
                    return redirect("caregiver_dashboard")
                else:
                    messages.error(request, "You are not registered as a caregiver.")
            else:
                messages.error(request, "Invalid caregiver credentials.")
        else:
            messages.error(request, "Invalid login details.")

    form = AuthenticationForm()
    return render(request, "care_giver.html", {"form": form})

# ✅ Logout
def user_logout(request):
    logout(request)
    messages.success(request, "Logged out successfully!")
    return redirect("home")

def care_giver(request):
    return render(request, "care_giver.html")

@login_required
def healthcare_status(request):
    return render(request, "healthcare_status.html")

@login_required
def message_dashboard(request):
    return render(request, "message_dashboard.html")

# ✅ Resident Profile Form (Fixed version)
@login_required
def resident_profile(request):
    resident, created = ResidentProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        print("Received POST data:", request.POST)  # Debugging line
        form = ResidentProfileForm(request.POST, request.FILES, instance=resident)
        
        if form.is_valid():
            form.save()
            print("Form saved successfully!")  # Debugging line
            return redirect("resident_dashboard")
        else:
            print("Form errors:", form.errors)  # Debugging line

    else:
        form = ResidentProfileForm(instance=resident)

    return render(request, "resident_profile.html", {"form": form, "resident": resident})


# ✅ Resident Dashboard
@login_required
def resident_dashboard(request):
    resident = ResidentProfile.objects.filter(user=request.user).first()
    return render(request, "resident_user_dashboard.html", {"resident": resident})




def healthcare_status(request):
    return render(request,"healthcare_status.html")
def update_health_status(request):
    resident = ResidentProfile.objects.filter(user=request.user).first()

    if not resident:
        return redirect("resident_profile")

    if request.method == "POST":
        selected_conditions = request.POST.getlist("conditions")  

        # Handle "Others" condition
        other_condition = request.POST.get("other_condition", "").strip()
        if "Others" in selected_conditions:
            selected_conditions.remove("Others")  # Remove "Others" placeholder
            if other_condition:  # If user entered a custom condition
                selected_conditions.append(other_condition)

        resident.conditions = ",".join(selected_conditions)  

        resident.allergies = request.POST.get("allergies", "")
        resident.medications = request.POST.get("medications", "")
        resident.medication_schedule = request.POST.get("medication_schedule", "")
        resident.doctor_name = request.POST.get("doctor_name", "")
        resident.doctor_phone = request.POST.get("doctor_phone", "")
        resident.reminder_time = request.POST.get("reminder_time", None)

        resident.save()
        return redirect("resident_dashboard")

    conditions_set = set(resident.conditions.split(",")) if resident.conditions else set()

    return render(request, "healthcare_status.html", {"resident": resident, "conditions_set": conditions_set})



import pytz  # Import timezone library
from datetime import datetime
from .models import MeetingRequest
def message_dashboard(request):
    # Get messages for the logged-in user
    messages = Message.objects.filter(user=request.user)

    # Fetch the resident profile
    try:
        resident = ResidentProfile.objects.get(user=request.user)
        reminder_time = resident.reminder_time  # This is a `time` field
        reminder_message = resident.reminder_message

        # ✅ Convert `reminder_time` (time-only) into a full `datetime`
        if reminder_time:
            today = now().date()  # Get today's date
            reminder_datetime = datetime.combine(today, reminder_time)  # Merge date & time
            reminder_datetime = make_aware(reminder_datetime)  # Make timezone-aware
        else:
            reminder_datetime = None

    except ResidentProfile.DoesNotExist:
        reminder_datetime = None
        reminder_message = None

    # Get current time in HH:MM format
    current_time = localtime(now()).strftime("%H:%M")

    # ✅ Check if it's time to send a reminder
    if reminder_datetime and reminder_datetime.strftime("%H:%M") == current_time:
        if not Notification.objects.filter(
            user=request.user,
            message=f"Reminder: {reminder_message}",
            timestamp__date=now().date()
        ).exists():
            Notification.objects.create(
                user=request.user,
                title="Medication Reminder",
                message=f"Reminder: {reminder_message} at {current_time}",
            )

    # Fetch notifications for display
    notifications = Notification.objects.filter(user=request.user).order_by("-timestamp")
    meeting_requests = MeetingRequest.objects.filter(resident__user=request.user).order_by("-request_date")

    return render(request, "message_dashboard.html", {
        "messages": messages,
        "notifications": notifications,
        "reminder_time": reminder_datetime.strftime("%H:%M") if reminder_datetime else None,
        "reminder_message": reminder_message,
        "current_time": current_time,  # Debugging
        "meeting_requests": meeting_requests,
    })
from django.http import JsonResponse
from home.models import Notification
from django.utils.timezone import localtime

def fetch_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-timestamp")
    notification_data = [
        {
            "title": n.title,
            "message": n.message,
            "timestamp": localtime(n.timestamp).strftime("%b %d, %Y %H:%M %p")
        }
        for n in notifications
    ]
    return JsonResponse({"notifications": notification_data})

from django.http import JsonResponse
from .models import Message, Notification

def delete_message(request, message_id):
    if request.method == "POST":
        try:
            message = Message.objects.get(id=message_id, user=request.user)
            message.delete()
            return JsonResponse({"success": True})
        except Message.DoesNotExist:
            return JsonResponse({"success": False, "error": "Message not found"})
    return JsonResponse({"success": False, "error": "Invalid request"})

def fetch_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by("-timestamp")[:10]
    data = [{"title": n.title, "message": n.message, "timestamp": n.timestamp.strftime("%Y-%m-%d %H:%M")} for n in notifications]
    return JsonResponse({"notifications": data})

def check_unread_messages(request):
    if request.user.is_authenticated:
        has_unread = Message.objects.filter(user=request.user, is_read=False).exists()
        return JsonResponse({"has_unread": has_unread})
    return JsonResponse({"error": "User not authenticated"}, status=403)
from django.http import JsonResponse
from .models import Message, Notification

def check_notifications(request):
    user = request.user

    # Check if there are any unread messages
    has_unread_messages = Message.objects.filter(user=user, is_read=False).exists()

    # Check if there are any new notifications (assuming all are 'unread' until viewed)
    has_new_notifications = Notification.objects.filter(user=user).exists()

    return JsonResponse({
        'has_unread_messages': has_unread_messages,
        'has_new_notifications': has_new_notifications
    })
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt
def send_emergency_sms(request):
    if request.method == "POST":
        try:
            resident = request.user.resident_profile  # Get resident profile

            emergency_name = resident.emergency_contact  # Emergency contact name
            emergency_number = resident.emergency_phone  # Emergency contact phone
            resident_name = resident.name  # Resident's name
            resident_phone = resident.phone  # Resident's phone

            if not emergency_number:
                return JsonResponse({"message": "No emergency contact number found!"}, status=400)

            # Custom Emergency Message
            message_body = f"🚨 Hi {emergency_name}, you are the emergency contact for {resident_name}. " \
                           f"{resident_name} needs immediate assistance. Please call them at {resident_phone}."

            # Fast2SMS API URL
            url = "https://www.fast2sms.com/dev/bulkV2"

            payload = {
                "route": "q",  # 'q' is for transactional messages
                "message": message_body,
                "language": "english",
                "flash": 0,
                "numbers": emergency_number
            }

            headers = {
                "authorization": "qUzHsfyLV70DAhG4cF1vgCxi8MkOIjYJuenQBK52WXbS6a3mZpGbJvomgy9UELDHpC1eWYOS2hil8wja",  # Replace with your API Key
                "Content-Type": "application/json"
            }

            # Send SMS
            response = requests.post(url, json=payload, headers=headers)

            return JsonResponse(response.json())

        except Exception as e:
            return JsonResponse({"message": f"Error: {str(e)}"}, status=500)
User = get_user_model()

def activate_caregiver(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        if default_token_generator.check_token(user, token):  
            user.is_active = True  
            user.save()
            messages.success(request, "Your account has been verified! You can now log in.")
            return redirect("care_giver")  # Redirect to login page
        else:
            messages.error(request, "Invalid or expired activation link.")
            return redirect("caregiver_signup")  
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        messages.error(request, "Invalid activation link.")
        return redirect("caregiver_signup")
from django.contrib.auth.forms import AuthenticationForm

def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            if user is not None:
                if not user.is_active:
                    messages.error(request, "Your account is not active!")
                    return redirect("user_login")

                # ✅ Ensure caregiver profile is approved before login
                if hasattr(user, "caregiver_profile") and not user.caregiver_profile.is_active:
                    messages.error(request, "Your caregiver profile is not approved yet!")
                    return redirect("user_login")

                login(request, user)

                # ✅ Redirect based on user type
                if user.user_type == "caregiver":
                    return redirect("caregiver_dashboard")
                return redirect("resident_dashboard")
            else:
                messages.error(request, "Invalid username or password!")
        else:
            messages.error(request, "Invalid login details.")

    form = AuthenticationForm()
    return render(request, "user_login.html", {"form": form})

from django.contrib import messages
from .models import CaregiverProfile
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import CaregiverProfile

User = get_user_model()
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CaregiverProfile

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CaregiverProfile

def verify_code(request):
    if request.method == "POST":
        email = request.POST.get("email")
        code = request.POST.get("code")

        # ✅ Use filter().first() instead of get() to avoid errors
        user_profile = CaregiverProfile.objects.filter(user__email=email, verification_code=code).first()

        if user_profile:
            if user_profile.is_verified:
                messages.success(request, "Your account is already verified. You can log in.")
                return redirect("care_giver")

            # ✅ Mark user as verified and activate their account
            user_profile.is_verified = True
            user_profile.user.is_active = True  # Activate the linked user account
            user_profile.verification_code = None  # Clear the verification code
            user_profile.user.save()
            user_profile.save()

            messages.success(request, "Verification successful! You can now log in.")
            return redirect("care_giver")
        else:
            messages.error(request, "Invalid verification code or email.")
            return redirect("verify_code")

    return render(request, "verify_code.html")
from django.shortcuts import render
from .models import CaregiverProfile

from django.shortcuts import render, get_object_or_404, redirect
from home.models import CaregiverProfile

def caregiver_profile(request):
    caregiver = get_object_or_404(CaregiverProfile, user=request.user)
    
    if request.method == "POST":
        print(request.POST)  # Debugging: See if data is coming through

        request.user.first_name = request.POST.get("first_name")
        request.user.last_name = request.POST.get("last_name")
        request.user.email = request.POST.get("email")
        request.user.save()

        caregiver.phone = request.POST.get("phone")
        caregiver.address = request.POST.get("address")
        caregiver.qualifications = request.POST.get("qualifications")
        caregiver.experience = request.POST.get("experience")
        caregiver.certifications = request.POST.get("certifications")
        caregiver.specialization = request.POST.get("specialization")
        caregiver.availability = request.POST.get("availability")
        caregiver.service_start_time = request.POST.get("service_start_time")
        caregiver.service_end_time = request.POST.get("service_end_time")
        caregiver.languages = request.POST.get("languages")
        caregiver.emergency_contact = request.POST.get("emergency_contact")
        caregiver.bio = request.POST.get("bio")

        if "profile_picture" in request.FILES:
            caregiver.profile_picture = request.FILES["profile_picture"]

        caregiver.save()

        print("Profile updated successfully!")  # Debugging: See if save() works

        return redirect("caregiver_dashboard")  # Redirect to refresh page
    
    return render(request, "caregiver_profile.html", {"caregiver_profile": caregiver})

@login_required
def caregiver_dashboard(request):
    try:
        caregiver_profile = CaregiverProfile.objects.get(user=request.user)
    except CaregiverProfile.DoesNotExist:
        caregiver_profile = None  # Handle the case when a profile doesn't exist

    context = {
        "caregiver_profile": caregiver_profile
    }
    return render(request, "caregiver_dashboard.html", context)

from django.shortcuts import render, get_object_or_404
from .models import ResidentProfile  # Ensure this is your model name

def resident_list(request):
    residents = ResidentProfile.objects.all()  # Fetch all residents
    return render(request, "caregiver_resident_list.html", {"residents": residents})

def resident_detail(request, resident_id):
    resident = get_object_or_404(ResidentProfile, id=resident_id)
    return render(request, "caregiver_resident_detail.html", {"resident": resident})

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import VisitorSignupForm
from django.contrib.auth.forms import AuthenticationForm


def visitors_signup(request):
    if request.method == "POST":
        form = VisitorSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.user_type = "visitor"
            user.is_visitor = True
            user.save()
            VisitorProfile.objects.create(user=user)
            return redirect("visitors_login")  # Redirect to login page after signup
    else:
        form = VisitorSignupForm()
    return render(request, "visitors_signup.html", {"form": form})

def visitors_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None and user.user_type == "visitor":
            login(request, user)
            return redirect("visitor_dashboard")  # Redirect to home or dashboard
        else:
            return render(request, "visitors_login.html", {"error": "Invalid credentials!"})
    return render(request, "visitors_login.html")

@login_required
def visitor_dashboard(request):
    visitor_profile = get_object_or_404(VisitorProfile, user=request.user)

    return render(request, 'visitor_dashboard.html', {
        'visitor_profile': visitor_profile
    })
@login_required
def visitor_profile(request):
    visitor_profile = get_object_or_404(VisitorProfile, user=request.user)

    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.save()

        visitor_profile.phone = request.POST.get('phone')
        visitor_profile.address = request.POST.get('address')  # Store address here
        
        if 'profile_picture' in request.FILES:
            visitor_profile.profile_picture = request.FILES['profile_picture']

        visitor_profile.save()
        return redirect('visitor_dashboard')  # Redirect to avoid resubmission issues

    return render(request, 'visitor_profile.html', {'visitor_profile': visitor_profile})
from .models import VisitorProfile, ResidentProfile, MeetingRequest
@login_required
def visitor_msg(request):
    user = request.user
    visitor_profile = VisitorProfile.objects.get(user=user)
    residents = ResidentProfile.objects.all()

    print("Residents:", residents)  # Debugging line to check residents' data

    if request.method == "POST":
        resident_id = request.POST.get("resident_id")
        date = request.POST.get("scheduled_date")
        time = request.POST.get("scheduled_time")

        resident = ResidentProfile.objects.get(id=resident_id)
        MeetingRequest.objects.create(
            visitor=visitor_profile,
            resident=resident,
            scheduled_date=date,
            scheduled_time=time,
            request_date=now()
        )

    meeting_requests = MeetingRequest.objects.filter(visitor=visitor_profile).order_by("-request_date")

    return render(request, "visitor_msg.html", {
        "visitor_profile": visitor_profile,
        "residents": residents,
        "meeting_requests": meeting_requests,
    })
import json
from django.http import JsonResponse

@login_required
def update_request_status(request, message_id):
    if request.method == "POST":
        try:
            # Parse the incoming JSON data
            data = json.loads(request.body)
            status = data.get('status')

            if status not in ['accepted', 'declined']:
                return JsonResponse({'error': 'Invalid status.'}, status=400)

            # Fetch the meeting request
            meeting_request = MeetingRequest.objects.get(id=message_id)

            # Ensure the current user is the resident
            if meeting_request.resident.user != request.user:
                return JsonResponse({'error': 'You are not authorized to update this request.'}, status=403)

            # Update the status of the meeting request
            meeting_request.status = status
            meeting_request.save()

            return JsonResponse({'success': True})

        except MeetingRequest.DoesNotExist:
            return JsonResponse({'error': 'Meeting request not found.'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
