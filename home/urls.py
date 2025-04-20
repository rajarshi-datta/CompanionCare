from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import delete_message, fetch_notifications, check_unread_messages
from .views import check_notifications
from .views import send_emergency_sms
from .views import caregiver_signup, activate_caregiver
from .views import verify_code
from .views import resident_list, resident_detail
from .views import visitors_signup, visitors_login
from .views import visitor_dashboard,visitor_profile,visitor_msg
urlpatterns = [
    path('', views.home, name='home'),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('user_login/', views.user_login, name='user_login'),  
    path('user_logout/', views.user_logout, name='user_logout'),
    path('resident_dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('message_dashboard/', views.message_dashboard, name='message_dashboard'),
    path('resident_profile/', views.resident_profile, name='resident_profile'),
    path('healthcare_status/', views.healthcare_status, name='healthcare_status'),
    path('care_giver/', views.care_giver, name='care_giver'),
    path('caregiver_signup/', views.caregiver_signup, name='caregiver_signup'),
    path('caregiver_login/', views.caregiver_login, name='caregiver_login'),
    path('caregiver_dashboard/', views.caregiver_dashboard, name='caregiver_dashboard'),
    path('dashboard/', views.resident_dashboard, name='resident_dashboard'),
    path('update_health_status/', views.update_health_status, name='update_health_status'),
    path("fetch_notifications/", fetch_notifications, name="fetch_notifications"),
    path('delete-message/<int:message_id>/', delete_message, name='delete_message'),
    path('fetch-notifications/', fetch_notifications, name='fetch_notifications'),
    path('check-unread-messages/', check_unread_messages, name='check_unread_messages'),
    path('check_notifications/', check_notifications, name='check_notifications'),
    path('send-emergency-sms/', send_emergency_sms, name='send_emergency_sms'),
    path("signup/", caregiver_signup, name="caregiver_signup"),
    path("activate/<uidb64>/<token>/", activate_caregiver, name="activate_caregiver"),
    path("verify_code/", verify_code, name="verify_code"),
    path('caregiver_profile/', views.caregiver_profile, name='caregiver_profile'),
    path("residents/", resident_list, name="resident_list"),
    path("residents/<int:resident_id>/", resident_detail, name="resident_detail"),
    path('visitors_signup/', visitors_signup, name='visitors_signup'),
    path('visitorslogin/', visitors_login, name='visitors_login'),
    path('visitor_dashboard/', visitor_dashboard, name='visitor_dashboard'),
    path('visitor_profile/', visitor_profile, name='visitor_profile'),
    path('visitor_msg/', views.visitor_msg, name='visitor_msg'),
    path('update-request-status/<int:message_id>/', views.update_request_status, name='update_request_status'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
