from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from .models import SentEmail, ReportedEmail, LegitimateEmail, LessonProgress, CustomUser, SentSMS, EditableSection, LegitimateSMS, AdminLesson
from django.core.mail import EmailMessage, get_connection
from django.views.decorators.http import require_POST
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from .forms import EmailPhishingQuizForm
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import requests

def set_no_cache_headers(response):
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@never_cache
def home(request):
    def get_content(section, default):
        obj = EditableSection.objects.filter(section=section).first()
        return obj.content if obj else default
    context = {
        'edit_inbox_title': get_content('edit_inbox_title', 'Phishing Inbox'),
        'edit_inbox_desc': get_content('edit_inbox_desc', 'Practice identifying suspicious emails in a realistic inbox simulation.'),
        'edit_flag_title': get_content('edit_flag_title', 'Red Flag Detection'),
        'edit_flag_desc': get_content('edit_flag_desc', 'Learn to spot the warning signs of phishing attempts through interactive examples.'),
        'edit_perf_title': get_content('edit_perf_title', 'Performance Tracking'),
        'edit_perf_desc': get_content('edit_perf_desc', 'Monitor your progress and see how your phishing detection skills improve over time.'),
        'edit_why_title': get_content('edit_why_title', 'Why Train Against Phishing?'),
        'edit_why_lead1': get_content('edit_why_lead1', 'Phishing attacks are on the rise, and training is your best defense.'),
        'edit_why_lead2': get_content('edit_why_lead2', 'Stay informed and protect yourself and your organization from cyber threats.'),
        'edit_why_lead3': get_content('edit_why_lead3', 'Join our phishing simulation training to enhance your skills and awareness.'),
        'edit_risk_title': get_content('edit_risk_title', 'The Risk is Real'),
        'edit_risk_desc': get_content('edit_risk_desc', '91% of cyber attacks start with a phishing email. It remains the most common way that organizations are compromised.'),
        'edit_aware_title': get_content('edit_aware_title', 'Awareness is Defense'),
        'edit_aware_desc': get_content('edit_aware_desc', 'Users who receive regular phishing simulation training are up to 50% less likely to fall for actual phishing attempts.'),
    }
    if request.user.is_authenticated:
        return redirect('dashboard')
    response = render(request, 'authentication/home.html', context)
    return set_no_cache_headers(response)

# Create your views here.
@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    response = render(request, 'authentication/register.html', {'form': form})
    return set_no_cache_headers(response)

@never_cache
def user_login(request):
    if request.user.is_authenticated:
        response = redirect('dashboard')
        return set_no_cache_headers(response)
    if request.method == 'POST':
        form = CustomUserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                response = redirect('dashboard')
                return set_no_cache_headers(response)
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = CustomUserLoginForm()
    response = render(request, 'authentication/login.html', {'form': form})
    return set_no_cache_headers(response)

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    progress = {}
    percent_complete = 0
    lessons = ['email_phishing_basics', 'suspicious_urls_domains', 'phishing_techniques_advance']
    if request.user.is_authenticated:
        for lesson in lessons:
            progress[lesson] = LessonProgress.objects.filter(user=request.user, lesson=lesson, completed=True).exists()
        completed_count = sum(progress.values())
        total_lessons = len(progress)
        percent_complete = int((completed_count / total_lessons) * 100) if total_lessons else 0
    def get_content(section, default):
        obj = EditableSection.objects.filter(section=section).first()
        return obj.content if obj else default
    context = {
        'percent_complete': percent_complete,
        'progress': progress,
        'edit_inbox_title': get_content('edit_inbox_title', 'Phishing Inbox'),
        'edit_inbox_desc': get_content('edit_inbox_desc', 'Practice identifying suspicious emails in a realistic inbox simulation.'),
        'edit_flag_title': get_content('edit_flag_title', 'Red Flag Detection'),
        'edit_flag_desc': get_content('edit_flag_desc', 'Learn to spot the warning signs of phishing attempts through interactive examples.'),
        'edit_perf_title': get_content('edit_perf_title', 'Performance Tracking'),
        'edit_perf_desc': get_content('edit_perf_desc', 'Monitor your progress and see how your phishing detection skills improve over time.'),
        'edit_why_title': get_content('edit_why_title', 'Why Train Against Phishing?'),
        'edit_why_lead1': get_content('edit_why_lead1', 'Phishing attacks are on the rise, and training is your best defense.'),
        'edit_why_lead2': get_content('edit_why_lead2', 'Stay informed and protect yourself and your organization from cyber threats.'),
        'edit_why_lead3': get_content('edit_why_lead3', 'Join our phishing simulation training to enhance your skills and awareness.'),
        'edit_risk_title': get_content('edit_risk_title', 'The Risk is Real'),
        'edit_risk_desc': get_content('edit_risk_desc', '91% of cyber attacks start with a phishing email. It remains the most common way that organizations are compromised.'),
        'edit_aware_title': get_content('edit_aware_title', 'Awareness is Defense'),
        'edit_aware_desc': get_content('edit_aware_desc', 'Users who receive regular phishing simulation training are up to 50% less likely to fall for actual phishing attempts.'),
    }
    response = render(request, 'authentication/dashboard.html', context)
    return set_no_cache_headers(response)

@login_required
def services(request):
    response = render(request, 'authentication/services.html')
    return set_no_cache_headers(response)

@staff_member_required
def email_phishing(request):
    users = CustomUser.objects.exclude(is_superuser=True)
    user_list = [
        {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'email': user.email
        }
        for user in users
    ]
    success = False
    sending_error = None
    if request.method == 'POST':
        subject = request.POST.get('subject')
        sender_name = request.POST.get('sender_name')
        sender_email = request.POST.get('sender_email')
        print('DEBUG: sender_email from POST:', sender_email)
        receiver_emails = request.POST.get('receiver_email')
        message = request.POST.get('message')
        is_real = request.POST.get('is_real') == 'on'
        from_email = settings.EMAIL_HOST_USER
        connection = None
        # Use Shoppee Shipping credentials if sender_email is shopie842@gmail.com or sender_name is Shoppee Shipping
        if sender_email == 'shopie842@gmail.com' or sender_name == 'Shoppee Shipping':
            shoppee = settings.EMAIL_ACCOUNTS.get('Shoppee Shipping')
            if shoppee:
                from_email = shoppee['EMAIL_HOST_USER']
                connection = get_connection(
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=shoppee['shopie842@gmail.com'],
                    password=shoppee['amlifjfxqpbxzfag'],
                    use_tls=settings.EMAIL_USE_TLS,
                    fail_silently=False
                )
        print('DEBUG: from_email:', from_email)
        print('DEBUG: connection username:', connection.username if connection else settings.EMAIL_HOST_USER)
        # Split and clean emails
        email_list = [e.strip() for e in receiver_emails.split(',') if e.strip()]
        try:
            for email_addr in email_list:
                email = EmailMessage(
                    subject,
                    message,
                    from_email,
                    [email_addr],
                    connection=connection if connection else None
                )
                email.send(fail_silently=False)
                SentEmail.objects.create(
                    sender_name=sender_name,
                    sender_email=from_email,
                    receiver_email=email_addr,
                    subject=subject,
                    message=message,
                    sent_by=request.user,
                    is_real=is_real
                )
            success = True
        except Exception as e:
            sending_error = str(e)
    response = render(request, 'authentication/email/email_phishing.html', {
        'user_list_json': json.dumps(user_list),
        'success': success,
        'sending_error': sending_error,
    })
    return set_no_cache_headers(response)

@staff_member_required
def sms_sender_view(request):
    users_with_phone = CustomUser.objects.exclude(is_superuser=True).exclude(phone_number__isnull=True).exclude(phone_number='')
    user_phone_list = [
        {
            'id': user.id,
            'name': f"{user.first_name} {user.last_name}".strip() or user.email,
            'phone_number': user.phone_number
        }
        for user in users_with_phone
    ]
    response = render(request, 'authentication/sms_send/sms_sender.html', {'users_with_phone': users_with_phone, 'user_phone_list_json': json.dumps(user_phone_list)})
    return set_no_cache_headers(response)

@login_required
def sent_email_inbox(request):
    sent_emails = SentEmail.objects.all().order_by('-sent_at')
    reported_emails = ReportedEmail.objects.all().order_by('-reported_at')
    from .models import LegitimateEmail
    legitimate_emails = LegitimateEmail.objects.all().order_by('-marked_at')
    return render(request, 'authentication/email/sent_inbox.html', {
        'sent_emails': sent_emails,
        'reported_emails': reported_emails,
        'legitimate_emails': legitimate_emails,
    })



@require_POST
@login_required
def report_sent_email(request, email_id):
    email = get_object_or_404(SentEmail, id=email_id)  # Allow reporting any email, not just user's own
    reason = request.POST.get('reason')
    details = request.POST.get('details', '')
    ReportedEmail.objects.create(
        reported_by=request.user,
        sender_name=email.sender_name,
        sender_email=email.sender_email,
        receiver_email=email.receiver_email,
        subject=email.subject,
        message=email.message,
        sent_at=email.sent_at,
        is_real=email.is_real,
        reason=reason,
        details=details
    )
    email.delete()
    return redirect('inbox')

@login_required
def reported_inbox(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')
    reported_emails = ReportedEmail.objects.filter(reported_by=request.user).order_by('-reported_at')
    return render(request, 'authentication/email/reported_inbox.html', {
        'reported_emails': reported_emails,
        'debug_user': request.user,  # Add user info for debugging
    })

@login_required
def inbox(request):
    if request.user.is_superuser:
        return redirect('admin_dashboard')

    sent_emails = SentEmail.objects.filter(receiver_email=request.user.email).order_by('-sent_at')
    reported_emails = ReportedEmail.objects.filter(reported_by=request.user).order_by('-reported_at')
    from .models import ReportedSMS, LegitimateEmail, LegitimateSMS
    user_sent_sms = SentSMS.objects.filter(sent_to=request.user).order_by('-sent_at')
    user_suspicious_sms = ReportedSMS.objects.filter(reported_by=request.user).order_by('-reported_at')
    legitimate_emails = LegitimateEmail.objects.filter(receiver_email=request.user.email).order_by('-marked_at')
    user_legit_sms = LegitimateSMS.objects.filter(marked_by=request.user).order_by('-marked_at')

    return render(request, 'authentication/email/sent_inbox.html', {
        'sent_emails': sent_emails,
        'reported_emails': reported_emails,
        'user_sent_sms': user_sent_sms,
        'user_suspicious_sms': user_suspicious_sms,
        'legitimate_emails': legitimate_emails,
        'user_legit_sms': user_legit_sms,
        'debug_user': request.user,
    })

def about(request):
    """Display the About page."""
    return render(request, 'authentication/about.html')


def mark_lesson_complete(request, lesson_name):
    if request.user.is_authenticated:
        LessonProgress.objects.update_or_create(
            user=request.user,
            lesson=lesson_name,
            defaults={'completed': True, 'completed_at': timezone.now()}
        )

@login_required
def email_phishing_basics(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        mark_lesson_complete(request, 'email_phishing_basics')
        from django.http import JsonResponse
        return JsonResponse({'success': True})
    lesson_urls = {
        'email_phishing_basics': 'email_phishing_basics',
        'suspicious_urls_domains': 'suspicious_urls_domains',
        'phishing_techniques_advance': 'phishing_techniques_advance',
    }
    from django.urls import reverse
    lesson_urls = {k: reverse(v) for k, v in lesson_urls.items()}
    return render(request, 'authentication/lessons/email_phishing_basics.html', {'lesson_urls': lesson_urls})

@login_required
def suspicious_urls_domains(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        mark_lesson_complete(request, 'suspicious_urls_domains')
        from django.http import JsonResponse
        return JsonResponse({'success': True})
    lesson_urls = {
        'email_phishing_basics': 'email_phishing_basics',
        'suspicious_urls_domains': 'suspicious_urls_domains',
        'phishing_techniques_advance': 'phishing_techniques_advance',
    }
    from django.urls import reverse
    lesson_urls = {k: reverse(v) for k, v in lesson_urls.items()}
    return render(request, 'authentication/lessons/suspicious_urls_domains.html', {'lesson_urls': lesson_urls})

@login_required
def phishing_techniques_advance(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        mark_lesson_complete(request, 'phishing_techniques_advance')
        from django.http import JsonResponse
        return JsonResponse({'success': True})
    return render(request, 'authentication/lessons/phishing_techniques_advance.html')

@login_required
def assessment(request):
    lesson_urls = {
        'email_phishing_basics': 'email_phishing_basics',
        'suspicious_urls_domains': 'suspicious_urls_domains',
        'phishing_techniques_advance': 'phishing_techniques_advance',
    }
    from django.urls import reverse
    lesson_urls = {k: reverse(v) for k, v in lesson_urls.items()}
    progress = {
        'email_phishing_basics': False,
        'suspicious_urls_domains': False,
        'phishing_techniques_advance': False,
    }
    if request.user.is_authenticated:
        for lesson in progress.keys():
            progress[lesson] = LessonProgress.objects.filter(user=request.user, lesson=lesson, completed=True).exists()
    completed_count = sum(progress.values())
    total_lessons = len(progress)
    percent_complete = int((completed_count / total_lessons) * 100) if total_lessons else 0
    return render(request, 'authentication/assessment.html', {
        'lesson_urls': lesson_urls,
        'progress': progress,
        'percent_complete': percent_complete
    })

def custom_404_view(request, exception=None):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        return redirect('home')

@staff_member_required
def admin_dashboard(request):
    users = CustomUser.objects.all()
    lessons = [
        'email_phishing_basics',
        'suspicious_urls_domains',
        'phishing_techniques_advance'
    ]
    user_progress = []
    for user in users:
        # Fetch lesson progress and scores for each lesson
        lesson1 = LessonProgress.objects.filter(user=user, lesson='email_phishing_basics').first()
        lesson2 = LessonProgress.objects.filter(user=user, lesson='suspicious_urls_domains').first()
        lesson3 = LessonProgress.objects.filter(user=user, lesson='phishing_techniques_advance').first()
        progress = {lesson: LessonProgress.objects.filter(user=user, lesson=lesson, completed=True).exists() for lesson in lessons}
        completed_count = sum(progress.values())
        total_lessons = len(progress)
        percent_complete = int((completed_count / total_lessons) * 100) if total_lessons else 0
        reported_emails = ReportedEmail.objects.filter(reported_by=user).order_by('-reported_at')
        from .models import ReportedSMS
        reported_sms = ReportedSMS.objects.filter(reported_by=user).order_by('-reported_at')
        reported_count = reported_emails.count() + reported_sms.count()
        user_progress.append({
            'user': user,
            'phone_number': user.phone_number,
            'progress': progress,
            'percent_complete': percent_complete,
            'reported_count': reported_count,
            'reported_emails': reported_emails,
            'reported_sms': reported_sms,
            'lesson1_score': lesson1.score if lesson1 and lesson1.score is not None else None,
            'lesson2_score': lesson2.score if lesson2 and lesson2.score is not None else None,
            'lesson3_score': lesson3.score if lesson3 and lesson3.score is not None else None,
        })
    return render(request, 'authentication/admin_dashboard.html', {'user_progress': user_progress, 'lessons': lessons})


@staff_member_required
def analytics(request):
    from .models import SentEmail, ReportedEmail, LessonProgress, CustomUser, SentSMS, ReportedSMS, LegitimateEmail, LegitimateSMS
    total_sent_emails = SentEmail.objects.count()
    total_sent_sms = SentSMS.objects.count()
    total_reported_emails = ReportedEmail.objects.count()
    total_reported_sms = ReportedSMS.objects.count()
    total_users = CustomUser.objects.count()
    total_completed = LessonProgress.objects.filter(completed=True).values('user').distinct().count()
    # New analytics for legitimate emails
    total_legit_emails_real = LegitimateEmail.objects.filter(is_real=True).count()
    total_legit_emails_fake = LegitimateEmail.objects.filter(is_real=False).count()
    # New analytics for reported emails
    total_reported_emails_real = ReportedEmail.objects.filter(is_real=True).count()
    total_reported_emails_fake = ReportedEmail.objects.filter(is_real=False).count()
    # SMS actions analytics
    sms_legit_real = LegitimateSMS.objects.filter(is_original_real=True).count()
    sms_legit_fake = LegitimateSMS.objects.filter(is_original_real=False).count()
    sms_reported_real = ReportedSMS.objects.filter(is_original_real=True).count()
    sms_reported_fake = ReportedSMS.objects.filter(is_original_real=False).count()
    return render(request, 'authentication/analytics.html', {
        'total_sent_emails': total_sent_emails,
        'total_sent_sms': total_sent_sms,
        'total_reported_emails': total_reported_emails,
        'total_reported_sms': total_reported_sms,
        'total_users': total_users,
        'total_completed': total_completed,
        'total_legit_emails_real': total_legit_emails_real,
        'total_legit_emails_fake': total_legit_emails_fake,
        'total_reported_emails_real': total_reported_emails_real,
        'total_reported_emails_fake': total_reported_emails_fake,
        'sms_legit_real': sms_legit_real,
        'sms_legit_fake': sms_legit_fake,
        'sms_reported_real': sms_reported_real,
        'sms_reported_fake': sms_reported_fake,
    })

@login_required
def user_sms_inbox(request):
    user_sms_messages = SentSMS.objects.none() # Default to empty queryset
    if request.user.is_authenticated and hasattr(request.user, 'phone_number') and request.user.phone_number:
        # Ensure you are querying based on the user's actual phone number
        user_sms_messages = SentSMS.objects.filter(receiver_number=request.user.phone_number).order_by('-sent_at')
    elif request.user.is_authenticated:
        messages.warning(request, "Please set your phone number in your profile to view your SMS inbox.")
    
    response = render(request, 'authentication/sms_send/user_sms_inbox.html', {
        'user_sms_messages': user_sms_messages
    })
    return set_no_cache_headers(response)

@login_required
def report_sent_sms(request, sms_id):
    sms = get_object_or_404(SentSMS, id=sms_id)
    if request.method == 'POST':
        reason = request.POST.get('reason')
        details = request.POST.get('details', '')
        from .models import ReportedSMS
        ReportedSMS.objects.create(
            reported_by=request.user,
            original_receiver_number=sms.receiver_number,
            original_message=sms.message,
            original_sent_at=sms.sent_at,
            is_original_real=sms.is_real,
            reason=reason,
            details=details,
            original_sender_email=sms.sent_by.email if sms.sent_by else ""
        )
        sms.delete()
        return redirect('inbox')
    return redirect('inbox')

def admin_home(request):
    if not request.user.is_superuser:
        return redirect('dashboard')
    # Handle AJAX POST for saving edits
    if request.method == 'POST' and request.headers.get('Content-Type') == 'application/json':
        data = json.loads(request.body)
        # Save each field to the EditableSection model
        EditableSection.objects.update_or_create(section='edit_inbox_title', defaults={'content': data.get('editInboxTitle', '')})
        EditableSection.objects.update_or_create(section='edit_inbox_desc', defaults={'content': data.get('editInboxDesc', '')})
        EditableSection.objects.update_or_create(section='edit_flag_title', defaults={'content': data.get('editFlagTitle', '')})
        EditableSection.objects.update_or_create(section='edit_flag_desc', defaults={'content': data.get('editFlagDesc', '')})
        EditableSection.objects.update_or_create(section='edit_perf_title', defaults={'content': data.get('editPerfTitle', '')})
        EditableSection.objects.update_or_create(section='edit_perf_desc', defaults={'content': data.get('editPerfDesc', '')})
        EditableSection.objects.update_or_create(section='edit_why_title', defaults={'content': data.get('editWhyTitle', '')})
        EditableSection.objects.update_or_create(section='edit_why_lead1', defaults={'content': data.get('editWhyLead1', '')})
        EditableSection.objects.update_or_create(section='edit_why_lead2', defaults={'content': data.get('editWhyLead2', '')})
        EditableSection.objects.update_or_create(section='edit_why_lead3', defaults={'content': data.get('editWhyLead3', '')})
        EditableSection.objects.update_or_create(section='edit_risk_title', defaults={'content': data.get('editRiskTitle', '')})
        EditableSection.objects.update_or_create(section='edit_risk_desc', defaults={'content': data.get('editRiskDesc', '')})
        EditableSection.objects.update_or_create(section='edit_aware_title', defaults={'content': data.get('editAwareTitle', '')})
        EditableSection.objects.update_or_create(section='edit_aware_desc', defaults={'content': data.get('editAwareDesc', '')})
        return JsonResponse({'success': True})
    # Fetch dynamic content for sections
    def get_content(section, default):
        obj = EditableSection.objects.filter(section=section).first()
        return obj.content if obj else default
    context = {
        'edit_inbox_title': get_content('edit_inbox_title', 'Phishing Inbox'),
        'edit_inbox_desc': get_content('edit_inbox_desc', 'Practice identifying suspicious emails in a realistic inbox simulation.'),
        'edit_flag_title': get_content('edit_flag_title', 'Red Flag Detection'),
        'edit_flag_desc': get_content('edit_flag_desc', 'Learn to spot the warning signs of phishing attempts through interactive examples.'),
        'edit_perf_title': get_content('edit_perf_title', 'Performance Tracking'),
        'edit_perf_desc': get_content('edit_perf_desc', 'Monitor your progress and see how your phishing detection skills improve over time.'),
        'edit_why_title': get_content('edit_why_title', 'Why Train Against Phishing?'),
        'edit_why_lead1': get_content('edit_why_lead1', 'Phishing attacks are on the rise, and training is your best defense.'),
        'edit_why_lead2': get_content('edit_why_lead2', 'Stay informed and protect yourself and your organization from cyber threats.'),
        'edit_why_lead3': get_content('edit_why_lead3', 'Join our phishing simulation training to enhance your skills and awareness.'),
        'edit_risk_title': get_content('edit_risk_title', 'The Risk is Real'),
        'edit_risk_desc': get_content('edit_risk_desc', '91% of cyber attacks start with a phishing email. It remains the most common way that organizations are compromised.'),
        'edit_aware_title': get_content('edit_aware_title', 'Awareness is Defense'),
        'edit_aware_desc': get_content('edit_aware_desc', 'Users who receive regular phishing simulation training are up to 50% less likely to fall for actual phishing attempts.'),
    }
    return render(request, 'admin_home.html', context)

from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required # Or staff_member_required, as appropriate

User = get_user_model()

@login_required
def get_selectable_users(request):
    import sys
    print('get_selectable_users called', file=sys.stderr)
    users = CustomUser.objects.exclude(is_superuser=True)
    user_list = []
    for user in users:
        name = f"{user.first_name} {user.last_name}".strip() or user.email
        print(f"User: {name} <{user.email}>", file=sys.stderr)
        user_list.append({
            'id': user.id,
            'name': name,
            'email': user.email
        })
    print(f"Returning {len(user_list)} users", file=sys.stderr)
    return JsonResponse({'users': user_list})

@require_POST
@login_required
def mark_email_legitimate(request, email_id):
    email = get_object_or_404(SentEmail, id=email_id)
    reason = request.POST.get('reason', '')
    details = request.POST.get('details', '')
    LegitimateEmail.objects.create(
        marked_by=request.user,
        sender_name=email.sender_name,
        sender_email=email.sender_email,
        receiver_email=email.receiver_email,
        subject=email.subject,
        message=email.message,
        sent_at=email.sent_at,
        is_real=email.is_real,
        reason=reason,
        details=details
    )
    email.delete()
    return redirect('inbox')

@require_POST
@login_required
def mark_sms_legitimate(request, sms_id):
    sms = get_object_or_404(SentSMS, id=sms_id)
    reason = request.POST.get('reason', '')
    details = request.POST.get('details', '')
    LegitimateSMS.objects.create(
        marked_by=request.user,
        original_receiver_number=sms.receiver_number,
        original_message=sms.message,
        original_sent_at=sms.sent_at,
        is_original_real=sms.is_real,
        reason=reason,
        details=details,
        original_sender_email=sms.sent_by.email if sms.sent_by else ""
    )
    sms.delete()
    return redirect('inbox')

@require_POST
@login_required
def mark_sms_legitimate_inbox(request, sms_id):
    sms = get_object_or_404(SentSMS, id=sms_id)
    from .models import LegitimateSMS
    LegitimateSMS.objects.create(
        marked_by=request.user,
        original_receiver_number=sms.receiver_number,
        original_message=sms.message,
        original_sent_at=sms.sent_at,
        is_original_real=sms.is_real,
        reason='',
        details='',
        original_sender_email=sms.sent_by.email if sms.sent_by else ""
    )
    sms.delete()
    return redirect('inbox')

@staff_member_required
def assessment_admin(request):
    lessons = AdminLesson.objects.all().order_by('order', 'id')
    total = lessons.count()
    completed = lessons.filter(completed=True).count()
    percent_complete = int((completed / total) * 100) if total else 0
    return render(request, 'authentication/assessment_admin.html', {
        'lessons': lessons,
        'percent_complete': percent_complete
    })

@require_POST
@login_required
def add_lesson(request):
    title = request.POST.get('title')
    description = request.POST.get('description', '')
    duration = request.POST.get('duration', '')
    lesson = AdminLesson.objects.create(title=title, description=description, duration=duration)
    return JsonResponse({'success': True, 'lesson': {
        'id': lesson.id,
        'title': lesson.title,
        'description': lesson.description,
        'duration': lesson.duration,
        'completed': lesson.completed
    }})

@require_POST
@login_required
def mark_lesson_completed(request):
    lesson_id = request.POST.get('lesson_id')
    lesson = AdminLesson.objects.get(id=lesson_id)
    lesson.completed = True
    lesson.save()
    return JsonResponse({'success': True})

@require_POST
@staff_member_required
def delete_lesson(request):
    lesson_id = request.POST.get('lesson_id')
    try:
        lesson = AdminLesson.objects.get(id=lesson_id)
        lesson.delete()
        return JsonResponse({'success': True})
    except AdminLesson.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Lesson not found'})

def lesson_detail(request, lesson_id):
    lesson = get_object_or_404(AdminLesson, id=lesson_id)
    return render(request, 'authentication/lesson_detail.html', {'lesson': lesson})

@login_required
def lesson4_social_media_phishing(request):
    if request.user.is_superuser:
        return redirect('dashboard')
    if request.method == 'POST':
        mark_lesson_complete(request, 'lesson4_social_media_phishing')
        from django.http import JsonResponse
        return JsonResponse({'success': True})
    return render(request, 'authentication/lessons/lesson4_social_media_phishing.html')

@require_POST
@login_required
def sms_phishing_api(request):
    try:
        data = json.loads(request.body)
        phone = data.get('receiver_number')
        message = data.get('message')
        is_real = data.get('is_real', False)
        if not phone or not message:
            return JsonResponse({'success': False, 'message': 'Missing phone or message.'}, status=400)
        numbers = [n.strip() for n in phone.split(',')] if ',' in phone else [phone]
        results = []
        for num in numbers:
            try:
                node_response = requests.post(
                    'http://localhost:3000/send-sms',
                    json={'number': num, 'message': message},
                    timeout=30
                )
                sent_to_user = CustomUser.objects.filter(phone_number=num).first()
                if node_response.status_code == 200:
                    SentSMS.objects.create(
                        receiver_number=num,
                        message=message,
                        sent_by=request.user,
                        is_real=is_real,
                        sent_to=sent_to_user
                    )
                    results.append({'number': num, 'status': 'success', 'message': node_response.text})
                else:
                    results.append({'number': num, 'status': 'failed', 'message': node_response.text})
            except requests.RequestException as e:
                results.append({'number': num, 'status': 'failed', 'message': f'Node.js SMS service error: {str(e)}'})
        overall_success = any(r['status'] == 'success' for r in results)
        return JsonResponse({'success': overall_success, 'results': results, 'message': 'See results for each number.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@never_cache
def admin_register(request):
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('admin_dashboard')
    else:
        form = AdminUserCreationForm()
    response = render(request, 'authentication/admin_register.html', {'form': form})
    return set_no_cache_headers(response)

@csrf_exempt
def save_quiz_score(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        lesson = data.get('lesson')
        score = data.get('score')
        if not lesson or score is None:
            return JsonResponse({'status': 'error', 'message': 'Missing lesson or score'}, status=400)
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)
        progress, created = LessonProgress.objects.get_or_create(
            user=user, lesson=lesson,
            defaults={'completed': True, 'score': score}
        )
        if not created:
            progress.score = score
            progress.completed = True
            progress.save()
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
