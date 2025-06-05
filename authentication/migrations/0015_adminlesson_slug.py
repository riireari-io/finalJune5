from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0014_set_email_phishing_first'),
    ]
    operations = [
        migrations.AddField(
            model_name='adminlesson',
            name='slug',
            field=models.CharField(max_length=100, unique=True, blank=True, null=True),
        ),
    ] 