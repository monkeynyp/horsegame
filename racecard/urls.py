from django.urls import path,include
from . import views
from django.views.generic import RedirectView
from .views import register, user_login, user_logout
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.recent_article, name='recent_article'),
    path('racecard/', views.racecard, name='racecard'),
        #Malaysia Pages
    path('racecard_my/', views.racecard_my, name='racecard_my'),
    path('view_by_member/', views.view_by_member, name='view_by_member'),
    path('blog/', views.recent_article, name='recent_article'),
    path('newsletter/', views.newsletter, name='newsletter'),
    path('send_article_email/', views.send_article_email, name='send_article_email'),
    path('contact/', views.contact, name='contact'),
    path('help/', views.help, name='help'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', user_logout, name='logout'),
    path('privacy/', views.privacy, name='privacy'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),
    path('facebookfeed/', views.facebook_feed, name='facebook_feed'),
    path('like_article/<int:article_id>/', views.like_article, name='like_article'),
    path('match_chart/', views.match_chart, name='match_chart'),
    path('data_update_console/', views.data_update_console, name='data_update_console'),
    path('update_race_result/', views.update_race_result, name='update_race_result'),
    path('lottory_predict/', views.lottory_predict, name='lottory_predict'),
    path('ichi_lotto/', views.ichi_lotto, name='ichi_lotto'),
    path('lotto_next_stat/', views.lotto_next_stat, name='lotto_next_stat'),
    path('update_lotto_tips/', views.update_lotto_tips, name='update_lotto_tips'),
    path('footballmatch/', views.football_match, name='football_match'),
    path('lotto_must_win/<int:id>/', views.lotto_must_win, name='lotto_must_win'),
    # Other URL patterns




    # Password reset URLs
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('submittips/',views.submit_tips, name='submit_tips'),
    path('member/', views.member, name='member'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


