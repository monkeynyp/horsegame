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
    @property
    def last_hit_rate(self):
        return UserTips.objects.filter(user=self.user, race_date=self.race_date, hit=1).count() / \
               UserTips.objects.filter(user=self.user, race_date=self.race_date).count()

    @property
    def last_profit(self):
        total_hit = UserTips.objects.filter(user=self.user, race_date=self.race_date, hit=1).count()
        total_dividend = UserTips.objects.filter(user=self.user, race_date=self.race_date).aggregate(total_dividend=Sum('dividend'))['total_dividend'] or 0
        if total_hit > 0:
            return total_dividend / total_hit * 10
        else:
            return 0
        
class UserScores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)

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

    def __str__(self):
        return self.title