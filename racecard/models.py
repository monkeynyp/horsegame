from django.db import models
from django.contrib.auth.models import User


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
    ratio = models.IntegerField(default=0)

class UserTips_jc(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the User model
    race_date = models.DateField()
    jockey = models.CharField(max_length=50)
    score = models.IntegerField()
    hit = models.IntegerField(default=0)
    dividend = models.FloatField(default=0)
        
class UserScores(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='score')
    total_records = models.IntegerField(default=0)
    total_hits = models.IntegerField(default=0)
    total_dividend = models.FloatField(default=0)
    hit_weight = models.FloatField(default=0)
    div_weight = models.FloatField(default=0)
    stars = models.CharField(max_length=25, null=True)
    stars1 = models.IntegerField(default=0)
    stars2 = models.IntegerField(default=0)

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
    image = models.ImageField(upload_to='racecard/images/')
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
    NextDraw_date = models.DateField(null=True)

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
    NextDraw_date = models.DateField(null=True)

    def __str__(self):
        return f"{self.Draw} - {self.Date}"

class Marksix_user_rec(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='marksix_rec')
    seq  = models.IntegerField()
    Draw = models.CharField(max_length=10)
    Date = models.DateField()
    No1 = models.IntegerField()
    No2 = models.IntegerField()
    No3 = models.IntegerField()
    No4 = models.IntegerField()
    No5 = models.IntegerField()
    No6 = models.IntegerField()
    No7 = models.IntegerField()
    Hit = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.Draw} - {self.Date}"

class FootballTeam(models.Model):
    team_name = models.CharField(max_length=100)
    attack_score = models.DecimalField(max_digits=3, decimal_places=1,default=1.0)
    defence_score = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    strategy_score = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    perf_score = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    desc_en = models.TextField(blank=True)
    desc_cn = models.TextField(blank=True)
    team_logos = models.ImageField(upload_to='team_logos/', blank=True)

    def __str__(self):
        return self.team_name

class FootballMatch(models.Model):
    match_date = models.DateTimeField()
    team_a = models.CharField(max_length=100)
    team_b = models.CharField(max_length=100)
    match_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    team_a_goal = models.IntegerField(default=0)
    team_b_goal = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.match_name} ({self.team_a} vs {self.team_b})"

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