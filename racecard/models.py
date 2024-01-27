from django.db import models

# Create your models here.

class UserTips(models.Model):
    username = models.CharField(max_length=50)
    race_date = models.DateField()
    race_no = models.IntegerField()
    horse_name = models.CharField(max_length=50)
    hit = models.IntegerField()
