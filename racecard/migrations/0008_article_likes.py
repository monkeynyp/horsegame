# Generated by Django 4.2.2 on 2024-03-12 12:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("racecard", "0007_userscores_div_weight_userscores_hit_weight"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="likes",
            field=models.IntegerField(default=0),
        ),
    ]