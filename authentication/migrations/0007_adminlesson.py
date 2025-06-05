from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0006_legitimatesms'),
    ]

    operations = [
        migrations.CreateModel(
            name='AdminLesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('duration', models.CharField(max_length=50, blank=True)),
                ('completed', models.BooleanField(default=False)),
            ],
        ),
    ] 