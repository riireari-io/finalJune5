from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.contrib.auth import get_user_model
from django.utils import timezone

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)
    
class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=50,blank=True)
    last_name = models.CharField(max_length=30,blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(unique=True,max_length=20, blank=True, null=True, help_text="Phone number must start with 63 followed by 10 digits (e.g., 639123456789)")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # PermissionsMixin provides default has_perm and has_module_perms.
    # If you want to keep the behavior where only superusers have all perms,
    # you can override these methods as you had them, or manage permissions via groups.
    def __str__(self):
        return self.email
    

class SentEmail(models.Model):
    sender_name = models.CharField(max_length=255)
    sender_email = models.EmailField()
    receiver_email = models.EmailField()
    subject = models.CharField(max_length=255)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    is_real = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} to {self.receiver_email}"


class ReportedEmail(models.Model):
    reported_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=255, blank=True, default="")
    sender_email = models.EmailField(blank=True, default="")
    receiver_email = models.EmailField(blank=True, default="")
    subject = models.CharField(max_length=255, blank=True, default="")
    message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    is_real = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, default="")
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reported: {self.subject} by {self.reported_by}"


class LessonProgress(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson = models.CharField(max_length=100)
    lesson_fk = models.ForeignKey('AdminLesson', on_delete=models.CASCADE, null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email} - {self.lesson if isinstance(self.lesson, str) else self.lesson.title} - {'Done' if self.completed else 'Not Done'}"


class SentSMS(models.Model):
    receiver_number = models.CharField(max_length=20)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    is_real = models.BooleanField(default=False)
    sent_to = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True, related_name='received_sms')

    def __str__(self):
        return f"SMS to {self.receiver_number}"
    
# In models.py
class ReportedSMS(models.Model):
    reported_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    original_receiver_number = models.CharField(max_length=20)
    original_message = models.TextField()
    original_sent_at = models.DateTimeField(null=True, blank=True)
    original_sender_email = models.EmailField(blank=True, default="")
    is_original_real = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, default="")
    reported_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reported SMS to {self.original_receiver_number} by {self.reported_by}"


class EditableSection(models.Model):
    SECTION_CHOICES = [
        ('features', 'Features'),
        ('why_train', 'Why Train'),
    ]
    section = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    content = models.TextField()

    def __str__(self):
        return self.section



class LegitimateEmail(models.Model):
    marked_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    sender_name = models.CharField(max_length=255, blank=True, default="")
    sender_email = models.EmailField(blank=True, default="")
    receiver_email = models.EmailField(blank=True, default="")
    subject = models.CharField(max_length=255, blank=True, default="")
    message = models.TextField(blank=True, default="")
    sent_at = models.DateTimeField(null=True, blank=True, default=timezone.now)
    is_real = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, default="")
    marked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Legitimate: {self.subject} to {self.receiver_email}"

class LegitimateSMS(models.Model):
    marked_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    original_receiver_number = models.CharField(max_length=20)
    original_message = models.TextField()
    original_sent_at = models.DateTimeField(null=True, blank=True)
    original_sender_email = models.EmailField(blank=True, default="")
    is_original_real = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, default="")
    details = models.TextField(blank=True, default="")
    marked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Legitimate SMS to {self.original_receiver_number} by {self.marked_by}"

class AdminLesson(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.CharField(max_length=50, blank=True)
    completed = models.BooleanField(default=False)
    order = models.IntegerField(default=0)
    slug = models.CharField(max_length=100, unique=True, blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.slug})"