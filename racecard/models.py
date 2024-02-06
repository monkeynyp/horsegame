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

class UserScores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)

class Article(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('tw', 'Chinese'),
        # Add more language choices as needed
    ]

    title = models.CharField(max_length=200)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)

    def __str__(self):
        return self.title