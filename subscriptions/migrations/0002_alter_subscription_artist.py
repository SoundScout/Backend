# Generated by Django 5.1.7 on 2025-03-27 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0001_initial'),
        ('users', '0003_user_is_active_user_is_staff_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='artist',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.artist'),
        ),
    ]
