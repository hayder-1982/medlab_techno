# Generated by Django 4.2 on 2024-10-13 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_patient_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]