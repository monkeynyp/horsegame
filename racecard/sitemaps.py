from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Race, StockInfo
from datetime import datetime

# Dictionary to store last modification dates for static pages
lastmod_dates = {
    'recent_article': datetime(2025, 2, 10),
    'racecard': datetime(2025, 2, 19),  # Update this date to the correct last modification date
    'racecard_vip': datetime(2025, 1, 18),  # Example update
    'jockey_king': datetime(2025, 1, 19),  # Example update
    # Add other static pages and their last modification dates here
}

class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return [
            'recent_article', 'racecard', 'racecard_vip', 'jockey_king', 'trainer_king',
            'view_by_member', 'newsletter', 'contact', 'help', 'privacy', 'disclaimer',
            'responsible', 'match_chart', 'data_update_console', 'lottory_predict',
            'ichi_lotto', 'lotto_next_stat', 'lotto_test', 'lotto_trio', 'lotto_longterm','stock_info'
        ]

    def location(self, item):
        return reverse(item)

    def lastmod(self, item):
        return lastmod_dates.get(item, datetime(2025, 1, 1))  # Default date if not found

class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Article.objects.all()

    def lastmod(self, obj):
        return obj.pub_date or datetime(2000, 1, 1)  # Default date if pub_date is None

class RaceSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Race.objects.all()

    def lastmod(self, obj):
        return obj.date or datetime(2000, 1, 1)  # Default date if date is None

class StockInfoSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return StockInfo.objects.all()

    def lastmod(self, obj):
        return obj.date or datetime(2000, 1, 1)  # Default date if date is None
