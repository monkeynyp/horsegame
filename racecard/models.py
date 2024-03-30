from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class UserTips(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    race_date = models.DateField()
    race_no = models.IntegerField()
    horse_no = models.IntegerField()
    horse_name = models.CharField(max_length=50)
    hit = models.IntegerField()
    dividend = models.FloatField(default=0)

class UserTips_my(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    race_date = models.DateField()
    race_no = models.IntegerField()
    horse_no = models.IntegerField()
    horse_name = models.CharField(max_length=50)
    hit = models.IntegerField()
    dividend = models.FloatField(default=0)
        
class UserScores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)
    hit_weight = models.FloatField(default=0)
    div_weight = models.FloatField(default=0)
    stars = models.CharField(max_length=25, null=True)

class UserScores_my(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score_my')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)
    hit_weight = models.FloatField(default=0)
    div_weight = models.FloatField(default=0)
    stars = models.CharField(max_length=25, null=True)

class Article(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('tw', 'Chinese'),
        # Add more language choices as needed
    ]

    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.CharField(max_length=50)
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title