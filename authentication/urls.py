from django.urls import path
from .views import *



urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),
    path('services/', services, name='services'),
    path('services/email_phishing/', email_phishing, name='email_phishing_service_page'),  # No trailing comma here
    path('services/sms_phishing/', sms_sender_view, name='sms_sender'),
    path('services/sms_phishing_api/', sms_phishing_api, name='sms_phishing_api'),
    path('inbox/', inbox, name='inbox'),
    path('report_sent_email/<int:email_id>/', report_sent_email, name='report_sent_email'),
    path('report_sent_sms/<int:sms_id>/', report_sent_sms, name='report_sent_sms'),
    path('about/', about, name='about'),
    path('assessment/', assessment, name='assessment'),
    path('assessment/email_phishing_basics/', email_phishing_basics, name='email_phishing_basics'),
    path('assessment/suspicious_urls_domains/', suspicious_urls_domains, name='suspicious_urls_domains'),
    path('assessment/phishing_techniques_advance/', phishing_techniques_advance, name='phishing_techniques_advance'),
    path('assessment/lesson4_social_media_phishing/', lesson4_social_media_phishing, name='lesson4_social_media_phishing'),
    path('admin-dashboard/', admin_dashboard, name='admin_dashboard'),
    path('analytics/', analytics, name='analytics'),
    path('reported_inbox/', reported_inbox, name='reported_inbox'),
    path('admin_home/', admin_home, name='admin_home'),
    path('email-phishing/', email_phishing, name='email_phishing'),
    path('ajax/get-selectable-users/', get_selectable_users, name='ajax_get_selectable_users'),
    path('mark_email_legitimate/<int:email_id>/', mark_email_legitimate, name='mark_email_legitimate'),
    path('mark-sms-legitimate/<int:sms_id>/', mark_sms_legitimate, name='mark_sms_legitimate'),
    path('assessment_admin/', assessment_admin, name='assessment_admin'),
    path('assessment_admin/add_lesson/', add_lesson, name='add_lesson'),
    path('assessment_admin/mark_lesson_completed/', mark_lesson_completed, name='mark_lesson_completed'),
    path('assessment_admin/delete_lesson/', delete_lesson, name='delete_lesson'),
    path('lesson/<int:lesson_id>/', lesson_detail, name='lesson_detail'),
    path('sms/mark_legitimate/<int:sms_id>/', mark_sms_legitimate_inbox, name='mark_sms_legitimate_inbox'),
    path('admin-register/', admin_register, name='admin_register'),
    path('save-quiz-score/', save_quiz_score, name='save_quiz_score'),
]



