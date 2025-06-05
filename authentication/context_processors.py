from .models import LessonProgress

def assessment_status(request):
    if request.user.is_authenticated:
        lessons = ['email_phishing_basics', 'suspicious_urls_domains', 'phishing_techniques_advance']
        completed = all(
            LessonProgress.objects.filter(user=request.user, lesson=lesson, completed=True).exists()
            for lesson in lessons
        )
        return {'assessment_complete': completed}
    return {'assessment_complete': False}
