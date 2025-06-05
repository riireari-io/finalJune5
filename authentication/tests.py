from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import LessonProgress

class LessonViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_lesson_views(self):
        self.client.login(username='testuser', password='testpass')
        lessons = [
            'email_phishing_basics',
            'suspicious_urls_domains',
            'phishing_techniques_advance',
        ]
        for lesson in lessons:
            url = reverse(lesson)
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(LessonProgress.objects.filter(user=self.user, lesson=lesson, completed=True).exists())

    def test_assessment_progress(self):
        self.client.login(username='testuser', password='testpass')
        LessonProgress.objects.create(user=self.user, lesson='email_phishing_basics', completed=True)
        response = self.client.get(reverse('assessment'))
        self.assertContains(response, 'Completed')

    def test_404_redirect(self):
        response = self.client.get('/nonexistent-url/', follow=True)
        self.assertIn(response.redirect_chain[-1][0], [reverse('dashboard'), reverse('home')])
