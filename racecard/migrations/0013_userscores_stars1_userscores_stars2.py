# Generated by Django 4.2.2 on 2024-09-12 14:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("racecard", "0012_usertips_ratio"),
    ]

    operations = [
        migrations.AddField(
            model_name="userscores",
            name="stars1",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="userscores",
            name="stars2",
            field=models.IntegerField(default=0),
        ),
    ]
