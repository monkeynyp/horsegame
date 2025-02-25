from django.urls import path, include
from . import views
from django.views.generic import RedirectView
from .views import register, user_login, user_logout, add_comment
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap, ArticleSitemap, RaceSitemap


sitemaps = {
    'static': StaticViewSitemap,
    'articles': ArticleSitemap,
    'races': RaceSitemap,
}





urlpatterns = [
    path('', views.recent_article, name='recent_article'),
    path('racecard/<int:race_id>/', views.racecard, name='racecard'),
    path('racecard_vip/', views.racecard_vip, name='racecard_vip'),
    path('jockey_king/', views.jockey_king, name='jockey_king'),
    path('trainer_king/', views.trainer_king, name='trainer_king'),
    path('view_by_member/', views.view_by_member, name='view_by_member'),
    path('blog/', views.recent_article, name='recent_article'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('send_article_email/', views.send_article_email, name='send_article_email'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('privacy/', views.privacy, name='privacy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('responsible/', views.responsible, name='responsible'),
    path('like_article/<int:article_id>/', views.like_article, name='like_article'),
    path('match_chart/', views.match_chart, name='match_chart'),
    path('data_update_console/', views.data_update_console, name='data_update_console'),
    path('update_race_result/', views.update_race_result, name='update_race_result'),
    path('lottory_predict/', views.lottory_predict, name='lottory_predict'),
    path('ichi_lotto/', views.ichi_lotto, name='ichi_lotto'),
    path('lotto_next_stat/', views.lotto_next_stat, name='lotto_next_stat'),
    path('update_lotto_tips/', views.update_lotto_tips, name='update_lotto_tips'),
    path('lotto_must_win/<int:id>/', views.lotto_must_win, name='lotto_must_win'),
    path('lotto_test/', views.lotto_test, name='lotto_test'),
    path('lotto_trio/', views.lotto_trio, name='lotto_trio'),
    path('lotto_longterm/', views.lotto_longterm, name='lotto_longterm'),
    path('race/<int:race_id>/add_comment/', views.add_comment, name='add_comment'),
    path('race/<int:race_id>/comments/', views.view_comments, name='view_comments'),
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type='text/plain')),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('article/<int:id>/', views.article_detail, name='article_detail'),
    path('race/<int:id>/', views.race_detail, name='race_detail'),
    path('add_stock_info/', views.add_stock_info, name='add_stock_info'),
    path('stock_info/', views.stock_info, name='stock_info'),
    path('racecard/', views.racecard_old),
 
    # Other URL patterns
    


    
    # Other URLs...

    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('submittips/', views.submit_tips, name='submit_tips'),
    path('member/', views.member, name='member'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
