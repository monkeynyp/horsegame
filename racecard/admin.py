from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import StockInfo,RaceComment,Race,UserTips, UserScores, Article, User, Marksix_hist,Marksix_user_rec,HorseInfo,Race_hist,LottoTrioSearch
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

class LottoTrioSearchAdmin(admin.ModelAdmin):
    list_display = ("Draw","Search_date","No1","No2","No3","Diff_days")

class Marksix_user_recAdmin(admin.ModelAdmin):
    list_display = ("user","Draw","Date","No1","No2","No3","No4","No5","No6","No7")


class Horse_InfoAdmin(admin.ModelAdmin):
    list_display = ("horse_name","horse_name_cn","band_no")

class Race_histAdmin(admin.ModelAdmin):
    list_display = ("band_no","index","rating")

class Race_Admin(admin.ModelAdmin):
    list_display = ("name","date","location")

class StockInfo_Admin(admin.ModelAdmin):
    list_display = ("title","content")
    
class RaceComment_Admin(admin.ModelAdmin):
    list_display = ("race_date","race_id","comment")

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email','get_groups')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

admin.site.register(LottoTrioSearch, LottoTrioSearchAdmin)
admin.site.register(UserTips, UserTipsAdmin)
admin.site.register(UserScores, UserScoresAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Marksix_hist, Marksix_histAdmin)
admin.site.register(Marksix_user_rec, Marksix_user_recAdmin)
admin.site.register(HorseInfo, Horse_InfoAdmin)
admin.site.register(Race_hist,Race_histAdmin)
admin.site.register(Race,Race_Admin)
admin.site.register(RaceComment,RaceComment_Admin)
admin.site.register(StockInfo,StockInfo_Admin)