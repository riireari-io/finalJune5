from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('authentication', '0008_seed_default_adminlessons'),
    ]
    operations = [
        migrations.AddField(
            model_name='adminlesson',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ] 