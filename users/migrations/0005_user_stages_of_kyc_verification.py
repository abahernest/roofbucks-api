# Generated by Django 4.1.7 on 2023-08-20 11:09

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_user_display_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='stages_of_kyc_verification',
            field=models.JSONField(default=users.models.stagesOfKycVerification),
        ),
    ]
