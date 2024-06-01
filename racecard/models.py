from django.db import models
from django.contrib.auth.models import User
from django_cryptography.fields import encrypt

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

class Marksix_hist(models.Model):
    Draw = models.CharField(max_length=255)
    Date = models.DateField()
    No1 = models.IntegerField()
    No2 = models.IntegerField()
    No3 = models.IntegerField()
    No4 = models.IntegerField()
    No5 = models.IntegerField()
    No6 = models.IntegerField()
    No7 = models.IntegerField()

    def __str__(self):
        return f"{self.Draw} - {self.Date}"


class MyModel(models.Model):
    name = models.CharField(max_length=100)
    secret_info = encrypt(models.CharField(max_length=100))

    def __str__(self):
        return self.name