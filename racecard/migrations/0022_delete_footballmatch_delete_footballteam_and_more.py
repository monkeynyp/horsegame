# Generated by Django 4.2.2 on 2024-10-28 14:23

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("racecard", "0021_usertips_horse_name_cn"),
    ]

    operations = [
        migrations.DeleteModel(
            name="FootballMatch",
        ),
        migrations.DeleteModel(
            name="FootballTeam",
        ),
        migrations.DeleteModel(
            name="UserTips_jc",
        ),
    ]
