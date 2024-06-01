from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import UserTips, UserScores, Article, User,UserTips_my, Marksix_hist
# Register your models here.
class UserTipsAdmin(admin.ModelAdmin):
    list_display = ("user","race_date","race_no","horse_no","horse_name","hit")

class UserTips_myAdmin(admin.ModelAdmin):
    list_display = ("user","race_date","race_no","horse_no","horse_name","hit")

class UserScoresAdmin(admin.ModelAdmin):
    list_display = ("user","total_records","total_hits","total_dividend","hit_weight")
class MyModelAdmin(admin.ModelAdmin):
    list_display = ("title","pub_date","user")
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title","pub_date","user")

class Marksix_histAdmin(admin.ModelAdmin):
    list_display = ("Draw","Date","No1","No2","No3","No4","No5","No6","No7")

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email','get_groups')

    def get_groups(self, obj):
        return ', '.join([group.name for group in obj.groups.all()])

    get_groups.short_description = 'Groups'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


admin.site.register(UserTips, UserTipsAdmin)
admin.site.register(UserScores, UserScoresAdmin)
admin.site.register(UserTips_my, UserTips_myAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Marksix_hist, Marksix_histAdmin)