# Generated by Django 4.2.2 on 2025-02-27 04:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("racecard", "0012_rename_hit_marksix_user_rec_hit35_and_more"),
    ]

    operations = [
        migrations.RenameField(
            model_name="marksix_user_rec",
            old_name="Hit35",
            new_name="Hit1",
        ),
        migrations.RenameField(
            model_name="marksix_user_rec",
            old_name="Hit45",
            new_name="Hit2",
        ),
        migrations.RenameField(
            model_name="marksix_user_rec",
            old_name="Hit55",
            new_name="Hit3",
        ),
        migrations.AddField(
            model_name="marksix_user_rec",
            name="Hit7",
            field=models.IntegerField(default=0),
        ),
    ]
