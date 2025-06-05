from django.db import migrations

def seed_admin_lessons(apps, schema_editor):
    AdminLesson = apps.get_model('authentication', 'AdminLesson')
    AdminLesson.objects.get_or_create(
        title="Understanding Phishing: A Modern Cyber Threat",
        defaults={
            'description': "Learn to identify common email phishing techniques and red flags.",
            'duration': "15 min"
        }
    )
    AdminLesson.objects.get_or_create(
        title="All About Email and SMS Phishing",
        defaults={
            'description': "Understand how to identify malicious URLs and fake domains.",
            'duration': "20 min"
        }
    )
    AdminLesson.objects.get_or_create(
        title="Case Study: The Rise of Phishing Attacks in the Philippines During the COVID-19 Pandemic",
        defaults={
            'description': "During the COVID-19 pandemic, the Philippines saw a dramatic increase in phishing and smishing attacks.",
            'duration': "25 min"
        }
    )

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0007_adminlesson'),
    ]
    operations = [
        migrations.RunPython(seed_admin_lessons),
    ] 