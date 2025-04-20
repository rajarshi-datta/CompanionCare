from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import ResidentProfile, CustomUser, CaregiverProfile,VisitorProfile

class UserSignupForm(UserCreationForm):
    full_name = forms.CharField(required=True, max_length=100)

    class Meta:
        model = CustomUser
        fields = ["username", "full_name", "email", "password1", "password2"]

class CaregiverSignupForm(UserCreationForm):
    full_name = forms.CharField(required=True, max_length=100)
    experience = forms.IntegerField(required=True, min_value=0)
    qualifications = forms.CharField(required=False, max_length=255)
    availability = forms.CharField(required=False, max_length=255)
    location = forms.CharField(required=False, max_length=255)

    class Meta:
        model = CustomUser
        fields = ["username", "full_name", "email", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.full_name = self.cleaned_data["full_name"]
        user.user_type = "caregiver"

        if commit:
            user.save()
            CaregiverProfile.objects.create(
                user=user,
                experience=self.cleaned_data["experience"],
                qualifications=self.cleaned_data["qualifications"],
                availability=self.cleaned_data["availability"],
                location=self.cleaned_data["location"],
            )
        return user

# ✅ New Resident Profile Form
class ResidentProfileForm(forms.ModelForm):
    class Meta:
        model = ResidentProfile
        fields = [
            "name", "age", "gender", "room", "photo", "phone",
            "emergency_contact", "emergency_phone",
            "meal", "assistance", "visit_schedule",
            "conditions", "allergies", "medications", "medication_schedule",
            "doctor_name", "doctor_phone", "reminder_time",  # ✅ Added health fields
        ]
        widgets = {
            "gender": forms.Select(choices=[("Male", "Male"), ("Female", "Female")]),
            "meal": forms.Select(choices=[("Veg", "Veg"), ("Non-Veg", "Non-Veg")]),
            "assistance": forms.Select(choices=[("None", "None"), ("Partial", "Partial"), ("Full", "Full")]),
            "visit_schedule": forms.Select(choices=[("Daily", "Daily"), ("Weekly", "Weekly"), ("Monthly", "Monthly")]),
            "conditions": forms.Textarea(attrs={"rows": 2}),
            "allergies": forms.Textarea(attrs={"rows": 2}),
            "medications": forms.Textarea(attrs={"rows": 3}),
            "medication_schedule": forms.Select(choices=[
                ("Morning", "Morning"),
                ("Afternoon", "Afternoon"),
                ("Night", "Night"),
            ]),
            "reminder_time": forms.TimeInput(attrs={"type": "time"}),  # ✅ Time input for medication reminder
        }
from django import forms

class VerificationForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter Verification Code'})
    )

class CaregiverProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = CaregiverProfile
        fields = [
            "phone", "address", "qualifications", "experience", "certifications",
            "specialization", "availability", "service_start_time", "service_end_time",
            "languages", "emergency_contact", "bio", "profile_picture"
        ]
        widgets = {
            "availability": forms.Select(choices=[
                ("full-time", "Full-Time"),
                ("part-time", "Part-Time"),
                ("on-call", "On-Call"),
            ]),
            "service_start_time": forms.TimeInput(attrs={"type": "time"}),
            "service_end_time": forms.TimeInput(attrs={"type": "time"}),
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Write a short bio about yourself"}),
        }
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, VisitorProfile

class VisitorSignupForm(UserCreationForm):
    full_name = forms.CharField(max_length=100, required=True, label="Full Name")
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = CustomUser
        fields = ["username", "email", "full_name", "password1", "password2","address"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.user_type = "visitor"
        user.is_visitor = True
        user.address=self.cleared["address"]
        if commit:
            user.save()
            VisitorProfile.objects.create(user=user, full_name=self.cleaned_data["full_name"])
        return user