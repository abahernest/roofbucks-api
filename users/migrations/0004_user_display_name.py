# Generated by Django 4.1.7 on 2023-03-14 23:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_stages_of_profile_completion_alter_user_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True, unique=True),
        ),
    ]