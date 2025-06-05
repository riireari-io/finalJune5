from django.db import migrations

def set_email_phishing_first(apps, schema_editor):
    AdminLesson = apps.get_model('authentication', 'AdminLesson')
    lesson = AdminLesson.objects.filter(title__icontains="email phishing").first()
    if lesson:
        lesson.order = 1
        lesson.save()
        # Reorder the rest
        others = AdminLesson.objects.exclude(id=lesson.id).order_by('order', 'id')
        for idx, l in enumerate(others, start=2):
            l.order = idx
            l.save()

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0013_lessonprogress_lesson_fk'),
    ]
    operations = [
        migrations.RunPython(set_email_phishing_first),
    ] 