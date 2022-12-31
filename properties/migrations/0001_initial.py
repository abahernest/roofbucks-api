# Generated by Django 4.1.3 on 2022-12-31 00:49

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import properties.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MediaAlbum',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'MediaAlbums',
            },
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True)),
                ('moderation_status', models.CharField(choices=[('PENDING', 'pending'), ('APPROVED', 'approved'), ('REJECTED', 'rejected')], default='PENDING', max_length=255)),
                ('archived', models.BooleanField(default=False)),
                ('completion_status', models.CharField(choices=[('IN-PROGRESS', 'construction in progress'), ('COMPLETED', 'contruction completed')], default='IN-PROGRESS', max_length=255)),
                ('apartment_type', models.CharField(max_length=255)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('percentage_discount', models.PositiveIntegerField(null=True)),
                ('promotion_closing_date', models.DateField(null=True)),
                ('promotion_type', models.CharField(blank=True, max_length=255)),
                ('other_deals', models.TextField(blank=True)),
                ('number_of_bedrooms', models.PositiveIntegerField(null=True)),
                ('number_of_toilets', models.PositiveIntegerField(null=True)),
                ('benefits', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None)),
                ('amenities', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None)),
                ('ERF_size', models.CharField(blank=True, max_length=256)),
                ('dining_area', models.CharField(blank=True, max_length=256)),
                ('cross_streets', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None)),
                ('landmarks', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=255), default=list, size=None)),
                ('floor_size', models.CharField(blank=True, max_length=255)),
                ('date_built', models.DateField(null=True)),
                ('price_per_share', models.PositiveBigIntegerField(null=True)),
                ('completion_cost', models.PositiveBigIntegerField(null=True)),
                ('completion_date', models.DateField(null=True)),
                ('percentage_completed', models.PositiveIntegerField(null=True)),
                ('zip_code', models.PositiveIntegerField(null=True)),
                ('total_number_of_shares', models.PositiveIntegerField(null=True)),
                ('total_property_cost', models.PositiveBigIntegerField(null=True)),
                ('expected_ROI', models.PositiveBigIntegerField(null=True)),
                ('area_rent_rolls', models.CharField(blank=True, max_length=255)),
                ('scheduled_stays', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.DateField(), default=list, size=None), default=list, size=None)),
                ('other_incentives', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('agent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('document_album', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='document_album', to='properties.mediaalbum')),
                ('image_album', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='image_album', to='properties.mediaalbum')),
            ],
            options={
                'db_table': 'Properties',
            },
        ),
        migrations.CreateModel(
            name='MediaFiles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=256, null=True)),
                ('image', models.ImageField(blank=True, default='', null=True, upload_to=properties.models.get_upload_path)),
                ('document', models.FileField(blank=True, null=True, upload_to=properties.models.get_upload_path_for_document)),
                ('media_type', models.CharField(choices=[('IMAGE', 'images'), ('DOCUMENT', 'documents')], default='IMAGE', max_length=256)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='media', to='properties.mediaalbum')),
            ],
            options={
                'db_table': 'MediaFiles',
            },
        ),
    ]
