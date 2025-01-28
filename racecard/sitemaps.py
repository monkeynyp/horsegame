from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Race

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'recent_article', 'racecard', 'racecard_vip', 'jockey_king', 'trainer_king',
            'view_by_member', 'newsletter', 'contact', 'help', 'privacy', 'disclaimer',
            'responsible', 'match_chart', 'data_update_console', 'lottory_predict',
            'ichi_lotto', 'lotto_next_stat', 'lotto_test', 'lotto_trio', 'lotto_longterm'
        ]

    def location(self, item):
        return reverse(item)

class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.pub_date

class RaceSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Race.objects.all()

    def lastmod(self, obj):
        return obj.date
