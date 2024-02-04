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

    def update_scores(self):
        # Update the score based on UserTips records
        self.total_records = UserTips.objects.filter(username=self.user).count()
        self.total_hits = UserTips.objects.filter(username=self.user, hit=1).count()
        self.save()