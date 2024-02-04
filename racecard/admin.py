from django.contrib import admin
from .models import UserTips, UserScores,Article
# Register your models here.
class UserTipsAdmin(admin.ModelAdmin):
    list_display = ("user","race_date","race_no","horse_no","horse_name","hit")

class UserScoresAdmin(admin.ModelAdmin):
    list_display = ("user","total_records","total_hits")
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title","pub_date","user")

admin.site.register(UserTips, UserTipsAdmin)
admin.site.register(UserScores)
admin.site.register(Article, ArticleAdmin)