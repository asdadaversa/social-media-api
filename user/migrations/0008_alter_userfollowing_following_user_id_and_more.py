# Generated by Django 5.0.1 on 2024-01-07 10:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("user", "0007_alter_userprofile_age_userfollowing_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="userfollowing",
            name="following_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="followers",
                to="user.userprofile",
            ),
        ),
        migrations.AlterField(
            model_name="userfollowing",
            name="user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="following",
                to="user.userprofile",
            ),
        ),
    ]