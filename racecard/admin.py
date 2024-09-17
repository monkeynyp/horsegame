from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import TW_lotto_hist,FootballMatch,FootballTeam,UserTips,UserTips_jc, UserScores, Article, User, Marksix_hist,Marksix_user_rec,HorseInfo,Race_hist
# Register your models here.
class UserTipsAdmin(admin.ModelAdmin):
    list_display = ("user","race_date","race_no","horse_no","horse_name","hit")

class UserTips_jcAdmin(admin.ModelAdmin):
    list_display = ("user","race_date","jockey","score")

class UserScoresAdmin(admin.ModelAdmin):
    list_display = ("user","total_records","total_hits","total_dividend","hit_weight")
class MyModelAdmin(admin.ModelAdmin):
    list_display = ("title","pub_date","user")
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title","pub_date","user")

class Marksix_histAdmin(admin.ModelAdmin):
    list_display = ("Draw","Date","No1","No2","No3","No4","No5","No6","No7")
class TW_lotto_histAdmin(admin.ModelAdmin):
    list_display = ("Draw","Date","No1","No2","No3","No4","No5","No6","No7")

class Marksix_user_recAdmin(admin.ModelAdmin):
    list_display = ("user","Draw","Date","No1","No2","No3","No4","No5","No6","No7")

class FootballTeamAdmin(admin.ModelAdmin):
    list_display = ("team_name","attack_score","defence_score","strategy_score","perf_score")

class FootballMatchAdmin(admin.ModelAdmin):
    list_display = ("match_date","team_a","team_b")

class Horse_InfoAdmin(admin.ModelAdmin):
    list_display = ("horse_name","horse_name_cn","band_no")

class Race_histAdmin(admin.ModelAdmin):
    list_display = ("band_no","index","rating")

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email','get_groups')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


admin.site.register(UserTips, UserTipsAdmin)
admin.site.register(UserScores, UserScoresAdmin)
admin.site.register(UserTips_jc, UserTips_jcAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Marksix_hist, Marksix_histAdmin)
admin.site.register(TW_lotto_hist, TW_lotto_histAdmin)
admin.site.register(Marksix_user_rec, Marksix_user_recAdmin)
admin.site.register(FootballTeam, FootballTeamAdmin)
admin.site.register(FootballMatch, FootballMatchAdmin)
admin.site.register(HorseInfo, Horse_InfoAdmin)
admin.site.register(Race_hist,Race_histAdmin)