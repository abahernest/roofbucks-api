# Generated by Django 4.1.7 on 2023-03-22 00:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('properties', '0006_property_approved_survey_plan_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='expected_ROI',
            field=models.FloatField(null=True),
        ),
    ]
