from apscheduler.schedulers.background import BackgroundScheduler
from django.utils.timezone import localtime,now
from django.core.mail import send_mail
from django.conf import settings
from datetime import time
from home.models import ResidentProfile, Notification
from datetime import timedelta


def medication_reminder():
    print("Scheduler is running...")

    ist_now = localtime()
    ist_now_no_seconds = time(ist_now.hour, ist_now.minute)
    print(f"Checking reminders for IST time: {ist_now_no_seconds}")

    # Avoid sending duplicate emails by checking `last_sent`
    one_minute_ago = now() - timedelta(minutes=1)
    residents = ResidentProfile.objects.filter(
        reminder_time=ist_now_no_seconds,
    ).exclude(last_sent__gte=one_minute_ago)  # Only send if not sent recently

    if not residents:
        print("No new reminders to send.")
    else:
        for resident in residents:
            if resident.user.email:
                message = (
                        f"Hi {resident.name},\n\n"
                        f"It's time to take your medicine: {resident.medications}.\n"
                        f"Please follow the prescribed schedule.\n\n"
                        f"Stay healthy!\n"
                        f"Best Regards,\nYour Care Team"
                )
                print(f"Attempting to send email to {resident.user.email}")

                try:
                    result = send_mail(
                        "Medication Reminder",
                        message,
                        settings.EMAIL_HOST_USER,
                        [resident.user.email],
                        fail_silently=False,
                    )

                    if result:
                        print(f"✅ Email sent to {resident.user.email}")
                        resident.last_sent = now()  # Update last sent time
                        resident.save()

                    else:
                        print(f"❌ Email sending failed for {resident.user.email}")

                    # **Save Notification for Dashboard**
                    Notification.objects.create(
                        user=resident.user,
                        title="Medication Reminder",
                        message=message
                    )
                    print(f"📌 Notification saved for {resident.user.username}")

                except Exception as e:
                    print(f"🚨 Email error: {e}")

            else:
                print(f"Skipping {resident.user.username} (No email found)")

    print("Scheduler execution completed.")

# APScheduler Initialization
scheduler = None

def start():
    global scheduler  # Use a single scheduler instance

    if scheduler and scheduler.running:
        print("⚠️ Scheduler is already running, skipping re-initialization.")
        return  # Prevent duplicate scheduler starts

    scheduler = BackgroundScheduler()
    
    # Check if the job already exists
    existing_jobs = scheduler.get_jobs()
    if any(job.id == "medication_reminder" for job in existing_jobs):
        print("⚠️ Job already exists, skipping...")
        return  # Don't add duplicate jobs

    scheduler.add_job(
        medication_reminder,
        'interval',
        minutes=1,
        id="medication_reminder",
        replace_existing=True
    )
    scheduler.start()
    print("✅ Scheduler started successfully")
