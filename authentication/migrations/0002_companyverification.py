# Generated by Django 4.1.3 on 2022-11-08 09:27

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authentication', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompanyVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_verified', models.BooleanField(default=False)),
                ('registration_number', models.CharField(max_length=65, unique=True, validators=[django.core.validators.MinLengthValidator(4)])),
                ('reference_number', models.CharField(max_length=12, unique=True, validators=[django.core.validators.MinLengthValidator(12)])),
                ('registered_company_name', models.CharField(max_length=500, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'CompanyVerification',
            },
        ),
    ]