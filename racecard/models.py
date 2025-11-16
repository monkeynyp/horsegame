from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


# Create your models here.

class UserTips(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    race_date = models.DateField()
    race_no = models.IntegerField()
    rank = models.IntegerField(default=0)
    jockey_score = models.IntegerField(default=0)
    trainer_score = models.IntegerField(default=0)
    horse_no = models.IntegerField()
    horse_name = models.CharField(max_length=50)
    horse_name_cn = models.CharField(max_length=50, null=True)
    jockey = models.CharField(max_length=25, null=True)
    trainer = models.CharField(max_length=25, null=True)
    hit = models.IntegerField()
    dividend = models.FloatField(default=0)
    win_div = models.FloatField(default=0)
    ratio = models.IntegerField(default=0)
    win_flag = models.BooleanField(default=False)
        
class UserScores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)
    hit_weight = models.FloatField(default=0)
    div_weight = models.FloatField(default=0)
    stars = models.CharField(max_length=25, null=True, blank=True)
    stars1 = models.IntegerField(default=0)
    stars2 = models.IntegerField(default=0)

class UserScores_my(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score_my')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)
    hit_weight = models.FloatField(default=0)
    div_weight = models.FloatField(default=0)
    stars = models.CharField(max_length=25, null=True, blank=True)

class Article(models.Model):
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('tw', 'Chinese'),
        # Add more language choices as needed
    ]

    title = models.CharField(max_length=50)
    content = models.TextField()
    image = models.ImageField(upload_to='racecard/images/')
    topics = models.CharField(max_length=15,default="Horse")
    pub_date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, default="Monkey")
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('article_detail', args=[str(self.id)])

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
    Price1 = models.CharField(max_length=30, null=True, default='NA')
    Price2 = models.CharField(max_length=30, null=True,default='NA')
    Price3 = models.CharField(max_length=30, null=True,default='NA')
    next_draw = models.CharField(max_length=255, null=True,default="NA")
    next_date = models.DateField(null=True)
        

    def __str__(self):
        return f"{self.Draw} - {self.Date}"

class TW_lotto_hist(models.Model):
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

class Marksix_user_rec(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marksix_rec')
    seq  = models.IntegerField()
    Draw = models.CharField(max_length=10,default="NA")
    Date = models.DateField()
    No1 = models.IntegerField()
    No2 = models.IntegerField()
    No3 = models.IntegerField()
    No4 = models.IntegerField()
    No5 = models.IntegerField()
    No6 = models.IntegerField()
    No7 = models.IntegerField(default=0)
    Hit1 = models.IntegerField(default=0)
    Hit2 = models.IntegerField(default=0)
    Hit3 = models.IntegerField(default=0)
    Hit4 = models.IntegerField(default=0)
    Hit5 = models.IntegerField(default=0)
    Hit6 = models.IntegerField(default=0)
    Hit7 = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.Draw} - {self.Date}"

class LottoTrioSearch(models.Model):
    Search_date = models.DateField()
    Draw = models.CharField(max_length=255)
    No1 = models.IntegerField()
    No2 = models.IntegerField()
    No3 = models.IntegerField()
    Diff_days = models.IntegerField(default=0)
    Freq = models.IntegerField(default=0)


    def __str__(self):
        return f"Draw: {self.Draw}, Search Date: {self.Search_date}"
    
class HorseInfo(models.Model):
    horse_name = models.CharField(max_length=100)
    horse_name_cn = models.CharField(max_length=100)
    band_no = models.CharField(max_length=20, unique=True)
    rating = models.IntegerField()
    rate_change = models.IntegerField()


    def __str__(self):
        return self.horse_name

class Race_hist(models.Model):
    band_no = models.ForeignKey(HorseInfo, to_field='band_no', on_delete=models.CASCADE)
    index = models.IntegerField()
    place = models.IntegerField()
    date = models.DateField()
    track = models.CharField(max_length=100)
    distance = models.IntegerField()
    good = models.CharField(max_length=100)
    race_class = models.CharField(max_length=100)
    draw = models.IntegerField()
    rating = models.IntegerField()
    trainer = models.CharField(max_length=100)
    jockey = models.CharField(max_length=100)
    lbw = models.CharField(max_length=50)
    win_odds = models.FloatField()
    act_wt = models.IntegerField()
    running_pos = models.CharField(max_length=100)
    finish_time = models.CharField(max_length=50)
    declar_horse_wt = models.IntegerField()
    gear = models.CharField(max_length=50)

    def __str__(self):
        return f"Race {self.index} at {self.place} on {self.date}"

class RaceComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    race_id = models.IntegerField()
    race_date = models.DateField(null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on race {self.race_id} dated {self.race_date}'

class Race(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    location = models.CharField(max_length=100)
    # Add other fields as necessary

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('race_detail', args=[str(self.id)])

class StockInfo(models.Model):
    title = models.CharField(max_length=200)
    stock_code = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    language = models.CharField(max_length=2, choices=[('en', 'English'), ('tw', 'Chinese')],default='tw')

    def __str__(self):
        return self.title